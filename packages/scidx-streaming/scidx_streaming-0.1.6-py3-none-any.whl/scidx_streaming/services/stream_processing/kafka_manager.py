import json
from aiokafka import AIOKafkaConsumer
import asyncio
import logging
import time
import pandas as pd
from aiokafka.helpers import create_ssl_context
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

    # Read processing configurations
    processing = stream.get("extras", {}).get("processing", {})
    data_key = processing.get("data_key", None)
    batch_mode = str(stream.get("extras", {}).get("batch_mode", "False")).lower() == "true"

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

                # Extract data if `data_key` is provided
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

            # Adaptive batching: Process when either threshold is met
            if len(messages) >= CHUNK_SIZE or time.time() - last_send_time >= batch_interval:
                if messages:
                    processed_messages = preprocess_messages(messages, batch_mode)
                    await process_and_send_data(processed_messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, None)
                    messages.clear()
                    last_send_time = time.time()

        # Final flush before shutdown
        if messages:
            processed_messages = preprocess_messages(messages, batch_mode)
            await process_and_send_data(processed_messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, None)

    except Exception as e:
        logger.error(f"Error in Kafka stream processing: {e}")
    finally:
        logger.info(f"Shutting down Kafka consumer for topic: {kafka_topic}")
        try:
            await consumer.stop()
        except Exception as shutdown_error:
            logger.error(f"Error shutting down Kafka consumer: {shutdown_error}")


def preprocess_messages(messages, batch_mode):
    """Preprocess messages before sending them to data processing."""
    if not messages:
        return []

    # Convert column-based batch format to row-based
    if batch_mode:
        try:
            df = pd.DataFrame(messages)
            if not df.empty and all(isinstance(v, list) for v in df.iloc[0].values):
                df = df.apply(pd.Series.explode).reset_index(drop=True)
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error expanding batch messages: {e}")
            return messages  # Return original messages if transformation fails

    return messages  # Return unchanged if batch_mode=False


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
