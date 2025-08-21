import logging
import asyncio
from confluent_kafka.admin import AdminClient
from fastapi import HTTPException
from .producer import Producer

logger = logging.getLogger(__name__)

async def create_stream(self, payload):
    """
    Create a new stream for the user.

    Parameters
    ----------
    payload : dict
        Payload containing keywords, filter_semantics, match_all flag, and optional authentication details.
    """
    logger.info("Searching data sources with keywords: %s", payload["keywords"])

    # Perform the search based on the match_all flag
    filtered_streams = await search_datasets_based_on_keywords(self, payload["keywords"], payload["match_all"], payload["server"])

    if not filtered_streams:
        raise HTTPException(status_code=404, detail="No data streams found matching the criteria.")

    # Get the next available stream ID
    stream_id = get_next_stream_id(self)

    # Extract optional username and password from the payload
    username = payload.get("username")
    password = payload.get("password")

    # Create a new Producer and start it asynchronously
    producer = Producer(
        streaming_client=self,
        filter_semantics=payload["filter_semantics"],
        data_streams=filtered_streams,
        stream_id=stream_id,
        username=username,
        password=password
    )

    asyncio.create_task(safe_producer_run(producer))

    logger.info("Stream created with ID: %s", producer.data_stream_id)
    involved_stream_ids = [stream["id"] for stream in filtered_streams]

    return producer, filtered_streams



async def search_datasets_based_on_keywords(self, keywords_list, match_all, server="local"):
    """
    Perform a search of data sources based on provided keywords and match_all flag.
    """
    if match_all and keywords_list:
        filtered_streams = self.search_datasets(terms=keywords_list, server=server)
        filtered_streams = filter_streams_with_all_keywords(filtered_streams, keywords_list)
    elif keywords_list:
        filtered_streams = []
        for keyword in keywords_list:
            streams = self.search_datasets(terms=keyword, server=server)
            filtered_streams.extend(streams)
        filtered_streams = list({stream["id"]: stream for stream in filtered_streams}.values())  # Remove duplicates
    else:
        filtered_streams = self.search_datasets(server=server)
    
    return filtered_streams


def get_kafka_topics_with_prefix(self):
    """
    Retrieve all Kafka topics starting with the specified prefix.
    """
    admin_client = AdminClient({'bootstrap.servers': f"{self.KAFKA_HOST}:{self.KAFKA_PORT}"})
    try:
        topics = admin_client.list_topics(timeout=10).topics.keys()
        return [topic for topic in topics if topic.startswith(self.KAFKA_PREFIX)]
    except Exception as e:
        logger.error(f"Error fetching Kafka topics: {e}")
        return []


def get_available_user_stream_ids(self):
    """
    Get a list of available stream IDs for a given user based on Kafka topics.
    """
    topics = get_kafka_topics_with_prefix(self)
    user_topic_ids = set()

    for topic in topics:
        if topic.startswith(f"{self.KAFKA_PREFIX}{self.user_id}_"):
            try:
                stream_id = int(topic.split(f"{self.KAFKA_PREFIX}{self.user_id}_")[1])
                user_topic_ids.add(stream_id)
            except (IndexError, ValueError):
                continue

    all_possible_ids = set(range(1, self.MAX_STREAMS + 1))
    return sorted(all_possible_ids - user_topic_ids)


def get_next_stream_id(self):
    """
    Get the next available stream ID for a given user.
    """
    available_ids = get_available_user_stream_ids(self)
    if not available_ids:
        raise Exception(f"No available stream IDs for user {self.user_id}. Maximum number of streams reached.")
    return available_ids[0]


async def safe_producer_run(producer):
    """
    Ensure the producer runs safely and handles any errors or exceptions gracefully.
    """
    try:
        await producer.run()
    except Exception as e:
        logger.error(f"Producer encountered an error: {e}")
    finally:
        logger.info(f"Producer {producer.data_stream_id} has stopped.")


def filter_streams_with_all_keywords(filtered_streams, keywords_list):
    """
    Filter streams to only include those that contain all keywords in their string representation.

    Parameters
    ----------
    filtered_streams : list of dict
        List of streams to filter.
    keywords_list : list of str
        List of keywords that must be present in each stream.

    Returns
    -------
    list of dict
        Filtered list of streams containing all keywords.
    """
    result = []
    for stream in filtered_streams:
        stream_str = str(stream).lower()  # Convert the entire stream to a lowercase string for case-insensitive matching
        if all(keyword.lower() in stream_str for keyword in keywords_list):
            result.append(stream)
    return result
