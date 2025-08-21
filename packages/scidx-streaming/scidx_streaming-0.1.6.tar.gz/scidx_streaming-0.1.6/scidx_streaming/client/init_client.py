from ndp_ep import APIClient
import jwt
import logging

logger = logging.getLogger(__name__)

class StreamingClient(APIClient):
    """
    A client to interact with the Streaming API and integrate with the PointOfPresence API.

    This class extends APIClient, inheriting its methods.

    Parameters
    ----------
    pop_client : APIClient
        An instance of the PointOfPresence API client.

    Attributes
    ----------
    base_url : str
        The base URL of the Streaming API.
    token : str
        The authentication token.
    user_id : str
        The extracted user ID from the token.
    KAFKA_HOST : str
        Kafka host retrieved from POP API connection details.
    KAFKA_PORT : int
        Kafka port retrieved from POP API connection details.
    KAFKA_PREFIX : str
        The prefix used for Kafka streams.
    MAX_STREAMS : int
        The maximum number of streams allowed.
    """

    def __init__(self, pop_client: APIClient):
        """
        Initialize the StreamingClient with an existing PointOfPresence APIClient.

        Parameters
        ----------
        pop_client : APIClient
            An existing APIClient instance.
        """
        if not isinstance(pop_client, APIClient):
            raise ValueError("`pop_client` must be an instance of APIClient.")

        # Initialize the parent class
        super().__init__(
            base_url=pop_client.base_url,
            token=pop_client.token,
            username=None,
            password=None,
        )

        self.base_url = pop_client.base_url
        self.session = pop_client.session
        self.token = pop_client.token

        # Kafka configurations with defaults
        self.KAFKA_HOST = None
        self.KAFKA_PORT = None
        self.KAFKA_PREFIX = "data_stream_"
        self.MAX_STREAMS = 10

        # Decode token to set user ID
        self.user_id = self._decode_user_id()

        # Fetch Kafka details
        self._fetch_kafka_details()

    def _decode_user_id(self):
        """
        Decode the token to extract the user ID.

        Returns
        -------
        str
            The extracted user ID from the token.
        """
        try:
            decoded_payload = jwt.decode(self.token, options={"verify_signature": False})
            user_id = decoded_payload.get("sub")
            if not user_id:
                raise ValueError("User ID not found in token.")
            logger.info(f"Extracted user ID: {user_id}")
            return user_id
        except jwt.DecodeError as e:
            logger.error(f"Error decoding token: {e}")
            raise ValueError("Invalid token provided.")

    def _fetch_kafka_details(self):
        """
        Fetch Kafka connection details from the POP API and set them as attributes.
        """
        try:
            kafka_details = self.get_kafka_details()
            if kafka_details.get("kafka_connection"):
                self.KAFKA_HOST = kafka_details["kafka_host"]
                self.KAFKA_PORT = kafka_details["kafka_port"]
                # Attempt to get the optional Kafka prefix and max streams
                self.KAFKA_PREFIX = kafka_details.get("kafka_prefix", self.KAFKA_PREFIX)
                self.MAX_STREAMS = kafka_details.get("max_streams", self.MAX_STREAMS)
                logger.info(f"Kafka details set: HOST={self.KAFKA_HOST}, PORT={self.KAFKA_PORT}, "
                            f"PREFIX={self.KAFKA_PREFIX}, MAX_STREAMS={self.MAX_STREAMS}")
            else:
                logger.warning("Kafka connection is not active. Streaming capabilities are disabled.")
                print("Warning: The Point of Presence is not configured with Kafka. Streaming capabilities are off.")
        except Exception as e:
            logger.error(f"Failed to fetch Kafka details. Streaming capabilities are disabled. Error: {e}")
            print("Error: Unable to fetch Kafka details. Streaming capabilities are off.")
