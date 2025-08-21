import json
from aiokafka import AIOKafkaConsumer
import asyncio
import logging
import time
import ssl
from aiokafka.helpers import create_ssl_context
from aiokafka.errors import UnknownTopicOrPartitionError
from ..data_cleaning import process_and_send_data
from ..compressor import decompress_data

# Create a logger
logger = logging.getLogger("aiokafka")

# Custom log filter
class KafkaLogFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        # Suppress repetitive Kafka warnings
        if "Topic ... is not available during auto-create initialization" in message:
            return False
        if "OffsetCommit failed for group" in message:
            return False
        if "Heartbeat session expired" in message:
            return False
        if "UnknownMemberIdError" in message:
            return False
        return True

# Apply the updated filter
logger.addFilter(KafkaLogFilter())

# Optionally, reduce log level for aiokafka
logger.setLevel(logging.ERROR)  # Suppress less severe logs


CHUNK_SIZE = 10000
TIME_WINDOW = 10  # seconds

async def process_kafka_stream(stream, filter_semantics, buffer_lock, send_data, loop, stop_event, username=None, password=None):
    kafka_host = stream.get("extras", {}).get("host", None)
    kafka_port = stream.get("extras", {}).get("port", None)
    kafka_topic = stream.get("extras", {}).get("topic", None)
    security_protocol = stream.get("extras", {}).get("security_protocol", None)
    sasl_mechanism = stream.get("extras", {}).get("sasl_mechanism", None)
    mapping = stream.get("extras", {}).get("mapping", None)
    processing = stream.get("extras", {}).get("processing", {})
    data_key = processing.get("data_key", None)
    info_key = processing.get("info_key", None)
    
    try:
        # Ensure all required parameters are available for SASL/SSL authentication
        if security_protocol and sasl_mechanism:
            if not username or not password:
                print(
                    f"Stream {kafka_topic} requires SASL authentication but no username/password provided. Skipping stream."
                )
                return
            
            # Create an SSL context
            ssl_context = create_ssl_context(
                cafile=None,  # Use default CA certificates
                certfile=None,  # Client certificates if required
                keyfile=None,  # Client key if required
            )
            consumer = AIOKafkaConsumer(
                kafka_topic,
                bootstrap_servers=f"{kafka_host}:{kafka_port}",
                security_protocol=security_protocol,
                sasl_mechanism=sasl_mechanism,
                sasl_plain_username=username,
                sasl_plain_password=password,
                ssl_context=ssl_context,
                auto_offset_reset='earliest',
                group_id=f"group_{kafka_topic}_{int(time.time())}"  # Unique group ID to avoid offset issues
            )
        else:
            # Default configuration for non-authenticated streams
            consumer = AIOKafkaConsumer(
                kafka_topic,
                bootstrap_servers=f"{kafka_host}:{kafka_port}",
                auto_offset_reset='earliest',
                group_id=f"group_{kafka_topic}_{int(time.time())}"  # Unique group ID to avoid offset issues
            )
            
        await consumer.start()
    except Exception as e:
        print(f"Error initializing Kafka consumer: {e}")
        return
    
    try:
        start_time = loop.time()
        last_send_time = time.time()
        messages = []
        additional_info = None
        timeout_counter = 0
        logging.info("STARTING CONSUMPTION!")
        while not stop_event.is_set():  # Stop event to handle graceful shutdown
            try:
                # Fetch message with a timeout to prevent blocking
                message = await asyncio.wait_for(consumer.getone(), timeout=TIME_WINDOW)
                
                try:
                    # Use decode_message to decode the Kafka message
                    data = decode_message(message.value)
                except ValueError as decode_error:
                    logger.error(f"Decoding failed: {decode_error}. Skipping message.")
                    continue  # Skip this message if decoding fails

                # if info_key:
                #     additional_info = data.get(info_key, {})

                # if data_key:
                #     data_key = data.get(data_key, {})
                
                messages.append(data)

                # Reset timeout counter when a message is received
                timeout_counter = 0

            except asyncio.TimeoutError:
                logger.info("No new messages received in TIME_WINDOW")
                timeout_counter += 1

            # If no new messages after multiple timeouts, stop the stream
            if timeout_counter >= 3:
                logger.info(f"No new messages received for {6 * TIME_WINDOW} seconds. Stopping the stream.")
                break
            
            # Send data after a chunk or time window is met
            if len(messages) >= CHUNK_SIZE or time.time() - last_send_time >= TIME_WINDOW:
                await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, additional_info)
                messages.clear()
                last_send_time = time.time()

        # Send any remaining messages before shutdown
        if messages:
            await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, additional_info)

    except Exception as e:
        print(f"Error in Kafka stream processing: {e}")
    finally:
        print(f"Shutting down Kafka consumer for topic: {kafka_topic}")
        try:
            await consumer.stop()  # Ensure the consumer stops properly
        except Exception as shutdown_error:
            print(f"Error shutting down Kafka consumer: {shutdown_error}")
        print(f"Kafka consumer for topic: {kafka_topic} has been shut down.")


def decode_message(message_value: bytes) -> dict:
    """
    Decode Kafka message by trying different decoding strategies.

    Parameters
    ----------
    message_value : bytes
        The raw message value from Kafka.

    Returns
    -------
    dict
        Decoded message as a dictionary.

    Raises
    ------
    ValueError
        If the message cannot be decoded.
    """
    try:
        # Try plain JSON decoding first
        data = json.loads(message_value.decode("utf-8"))
        return data
    except UnicodeDecodeError as e:
        pass
        
    try:
        # Try plain JSON decoding first
        data = json.loads(message_value)
        return data
    except UnicodeDecodeError as e:
        pass

    try:
        # Attempt to decompress the message (e.g., Blosc)
        data = decompress_data(message_value)
        return data
    except Exception as decompression_error:
        print(f"Decompression failed: {decompression_error}. Logging raw data.")

    raise ValueError("Failed to decode the message using all strategies.")

