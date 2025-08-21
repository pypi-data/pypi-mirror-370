import json
from aiokafka import AIOKafkaConsumer
import asyncio
import logging
import time
from aiokafka.helpers import create_ssl_context
import pandas as pd
from ..data_cleaning import process_and_send_data
from ..compressor import decompress_data

# Create a logger
logger = logging.getLogger("aiokafka")
logger.setLevel(logging.ERROR)

class KafkaLogFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        suppressed_messages = [
            "Topic ... is not available during auto-create initialization",
            "OffsetCommit failed for group",
            "Heartbeat session expired",
            "UnknownMemberIdError"
        ]
        return not any(msg in message for msg in suppressed_messages)

logger.addFilter(KafkaLogFilter())

CHUNK_SIZE = 10000  # Process in chunks when needed

async def process_kafka_stream(
    stream, filter_semantics, buffer_lock, send_data, loop, stop_event, username=None, password=None
):
    kafka_host = stream.get("extras", {}).get("host", None)
    kafka_port = stream.get("extras", {}).get("port", None)
    kafka_topic = stream.get("extras", {}).get("topic", None)
    security_protocol = stream.get("extras", {}).get("security_protocol", None)
    sasl_mechanism = stream.get("extras", {}).get("sasl_mechanism", None)
    mapping = stream.get("extras", {}).get("mapping", None)

    # Configurable parameters
    auto_offset_reset = stream.get("extras", {}).get("auto_offset_reset", "earliest")  
    time_window = float(stream.get("extras", {}).get("time_window", 10))  # Default to 10 sec
    batch_interval = float(stream.get("extras", {}).get("batch_interval", 1))  # Default batch interval: 1 sec

    # Processing parameters
    batch_mode = str(stream.get("extras", {}).get("batch_mode", "False")).lower() == "true"
    processing = stream.get("extras", {}).get("processing", {})
    data_key = processing.get("data_key", None)

    try:
        if security_protocol and sasl_mechanism:
            if not username or not password:
                logger.error(f"Stream {kafka_topic} requires SASL authentication but no credentials provided. Skipping.")
                return
            ssl_context = create_ssl_context()
            consumer = AIOKafkaConsumer(
                kafka_topic,
                bootstrap_servers=f"{kafka_host}:{kafka_port}",
                security_protocol=security_protocol,
                sasl_mechanism=sasl_mechanism,
                sasl_plain_username=username,
                sasl_plain_password=password,
                ssl_context=ssl_context,
                auto_offset_reset=auto_offset_reset,
                group_id=f"group_{kafka_topic}_{int(time.time())}",  # Ensure a fresh session
                enable_auto_commit=False,  # Avoid offset mismanagement
            )
        else:
            consumer = AIOKafkaConsumer(
                kafka_topic,
                bootstrap_servers=f"{kafka_host}:{kafka_port}",
                auto_offset_reset=auto_offset_reset,
                group_id=f"group_{kafka_topic}_{int(time.time())}",
                enable_auto_commit=False,
            )

        await consumer.start()
    except Exception as e:
        logger.error(f"Error initializing Kafka consumer: {e}")
        return

    try:
        logger.info(f"Starting Kafka message consumption for topic: {kafka_topic}")
        messages = []
        last_send_time = time.time()
        timeout_counter = 0

        while not stop_event.is_set():
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=time_window)
                
                try:
                    data = decode_message(message.value)
                except ValueError as decode_error:
                    logger.error(f"Decoding failed: {decode_error}. Skipping message.")
                    continue

                # Extract data from specified key if provided
                if data_key and isinstance(data, dict) and data_key in data:
                    data = data[data_key]

                messages.append(data)
                timeout_counter = 0  # Reset timeout counter when receiving data

            except asyncio.TimeoutError:
                timeout_counter += 1
                logger.info(f"No messages received for {timeout_counter * time_window} sec.")

            # Stop the consumer after multiple timeouts
            if timeout_counter >= 30:
                logger.info(f"Stopping stream {kafka_topic} due to inactivity.")
                break

            # Adaptive batching: Process messages at batch interval
            if len(messages) >= CHUNK_SIZE or time.time() - last_send_time >= batch_interval:
                if messages:
                    # Flatten batch messages if batch_mode is enabled
                    if batch_mode:
                        flattened_messages = []
                        for msg in messages:
                            if isinstance(msg, list):
                                flattened_messages.extend(msg)
                            elif isinstance(msg, dict) and all(isinstance(v, list) for v in msg.values()):
                                # Convert column-based batch to row-based format
                                try:
                                    df_temp = pd.DataFrame.from_dict(msg)
                                    flattened_messages.extend(df_temp.to_dict(orient="records"))
                                except Exception as e:
                                    logger.error(f"Error processing column-based batch format: {e}")
                            else:
                                flattened_messages.append(msg)
                        messages = flattened_messages

                    await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, None)
                    messages.clear()
                    last_send_time = time.time()

        # Final flush before shutdown
        if messages:
            if batch_mode:
                flattened_messages = []
                for msg in messages:
                    if isinstance(msg, list):
                        flattened_messages.extend(msg)
                    elif isinstance(msg, dict) and all(isinstance(v, list) for v in msg.values()):
                        try:
                            df_temp = pd.DataFrame.from_dict(msg)
                            flattened_messages.extend(df_temp.to_dict(orient="records"))
                        except Exception as e:
                            logger.error(f"Error processing column-based batch format: {e}")
                    else:
                        flattened_messages.append(msg)
                messages = flattened_messages

            await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, None)

    except Exception as e:
        logger.error(f"Error in Kafka stream processing: {e}")
    finally:
        logger.info(f"Shutting down Kafka consumer for topic: {kafka_topic}")
        try:
            await consumer.stop()
        except Exception as shutdown_error:
            logger.error(f"Error shutting down Kafka consumer: {shutdown_error}")



def decode_message(message_value: bytes) -> dict:
    """Decode Kafka message."""
    try:
        return json.loads(message_value.decode("utf-8"))
    except UnicodeDecodeError:
        pass
    try:
        return json.loads(message_value)
    except UnicodeDecodeError:
        pass
    try:
        return decompress_data(message_value)
    except Exception as decompression_error:
        logger.error(f"Decompression failed: {decompression_error}")
    raise ValueError("Failed to decode the message.")
