import logging
from typing import List, Dict, Optional
from scidx_streaming.services.stream_manager import create_stream

logger = logging.getLogger(__name__)

async def create_kafka_stream(
    self, 
    keywords: List[str], 
    filter_semantics: Optional[List[str]] = [], 
    match_all: Optional[bool] = True, 
    username: Optional[str] = None, 
    password: Optional[str] = None,
    server: Optional[str] = "local"
) -> Dict:
    """
    Simplified version of create_stream.

    Parameters
    ----------
    keywords : list
        Keywords to search for data sources.
    filter_semantics : list, optional
        Optional filtering semantics for the datasets.
    match_all : bool, optional
        If True, all keywords must match. Default is True.
    username : str, optional
        Optional Kafka username for authentication.
    password : str, optional
        Optional Kafka password for authentication.

    Returns
    -------
    dict
        Metadata about the found datasets.
    """

    logger.info("Searching datasets with keywords: %s", keywords)

    try:

        if not self.user_id:
            raise ValueError("User ID not available in the StreamingClient instance.")

        # Prepare payload with optional username and password
        payload = {
            "keywords": keywords,
            "filter_semantics": filter_semantics,
            "match_all": match_all,
            "server": server
        }

        if username:
            payload["username"] = username
        if password:
            payload["password"] = password

        # Create the stream with the provided parameters
        producer, dataset_list = await create_stream(self, payload)        

        if producer:
            topic = producer.data_stream_id

        logger.info("Topic %s.", payload.get("topic", ""))

        self.server = server if server and server != "global" else "local"

        payload = {
            "topic": topic,
            "keywords": ",".join(keywords),
            "filter_semantics": ",".join(filter_semantics),
            "match_all": str(match_all),
            "status": "active",
            "format": "stream",
            "url": f"http://{self.KAFKA_HOST}:{self.KAFKA_PORT}",
            "description": f"Kafka stream for topic {topic}. This stream is derived from the keywords: {', '.join(keywords)}. It is filtered by semantics: {', '.join(filter_semantics)}. All keywords must match: {match_all}. The stream status is active.",
            "name": f"derived {topic}"
        }
        
        for dataset in dataset_list:
            logger.info("Updating dataset with %s", str(dataset))
            
            patch_response = self.patch_general_dataset(
                dataset_id=dataset['id'],
                server=self.server,
                data={"resources": [payload]}
            )

            logger.info("Patch response: %s", patch_response)
             
        return producer
    
    except ValueError as e:
        logger.error(f"Error while searching datasets: {e}")
        return {"error": str(e)}
