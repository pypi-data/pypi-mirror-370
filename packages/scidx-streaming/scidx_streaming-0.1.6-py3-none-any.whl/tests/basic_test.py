import asyncio
from http.client import HTTPException
import logging
import pytest
from scidx_streaming.client.init_client import StreamingClient
from ndp_ep import APIClient
import time

# Constants
API_URL = "http://155.101.6.191:8003"
USERNAME = "placeholder@placeholder.com"
PASSWORD = "placeholder"
TOKEN = "placeholder"

streams_to_test = [
    #{
   #     "keywords": "pinguintest,CSV",
    #    "match_all": True,
   #     "filter_semantics": [
   #         "window_filter(5, mean, fixed acidity > 8.7)",
   #         "residual sugar > 1.5",
    #        "IF window_filter(9, sum, residual sugar > 20) THEN alert = fixed acidity*100 ELSE fixed acidity = fixed acidity*1000",
   #         "IF alert IN ['blue'] THEN residual sugar = fixed acidity*100"
   #     ],
  #  },
    #{
   #     "keywords": "pinguintest,CSV",
   #     "match_all": True,
    #    "filter_semantics": [
    #        "fixed acidity > 7.5",
   #         "residual sugar > 1.5",
   #         "IF fixed acidity > 8 AND residual sugar <= 2 THEN alert = red ELSE alert = blue"
  #      ],
   # },
   # {
   #     "keywords": "cuphead", 
   #     "match_all": True,
   #     "filter_semantics": [
   #         "IF Rad > 120 THEN alert = red ELSE alert = blue",
    #        "IF alert IN ['red'] THEN Rad = Rad*Rad",
   #     ],
    #},
    # {
    #     "keywords": "existing_stream_test,kafka",
    #     "match_all": True,
    #     "filter_semantics": []
    # },
    #  {
    #      "keywords": "earthscope_kafka_gnss_observations,kafka",
    #      "match_all": True,
    #      "filter_semantics": [],
    #      "username": 'placeholder',
    #      "password":'placeholder'
    #  }
    {
         "keywords": "sumaiya_test",
         "match_all": True,
         "filter_semantics": ["IF ozone_concentration > 30 THEN alert = HIGH ELSE alert = LOW"],
    }
    # {
    #     "keywords": "pokemon",
    #     "match_all": True,
    #     "filter_semantics": ["name IN ['sturdy', 'damp', 'limber']", "IF name = 'sturdy' THEN alert = red"],
    # },
    # {
    #     "keywords": "pinguintest123,TXT",
    #     "match_all": True,
    #     "filter_semantics": [
    #         "x > -1",
    #         "IF x > -0.005 THEN x = y-20 ELSE x = 30+x",
    #         "IF x > 0 THEN alert = 2000 ELSE alert = 9999*x",
    #     ],
    # }
]

@pytest.mark.asyncio
async def test_create_and_consume_multiple_kafka_streams():
    """
    Test creating multiple Kafka streams, consuming messages from the topics, and deleting the streams.
    """
    # Initialize the PointOfPresence APIClient
    client = APIClient(base_url=API_URL, token=TOKEN)

    # Initialize the StreamingClient
    streaming = StreamingClient(client)

    # Validate Kafka connection
    if not streaming.KAFKA_HOST or not streaming.KAFKA_PORT:
        print("Kafka connection is not available. Skipping streaming tests.")
        return

    # Show Kafka details
    print("Kafka Connection Details:")
    print(f"KAFKA_HOST: {streaming.KAFKA_HOST}")
    print(f"KAFKA_PORT: {streaming.KAFKA_PORT}")



    # Show the user ID
    print(f"User ID: {streaming.user_id}")

    await streaming.delete_stream('all')

    for stream_config in streams_to_test:
        # Step 1: Create the Kafka stream
        try:
            stream = await streaming.create_kafka_stream(
                keywords=stream_config.get("keywords", "").split(","),
                filter_semantics=stream_config.get("filter_semantics", []),
                match_all=stream_config.get("match_all", True),
                username=stream_config.get("username", None),
                password=stream_config.get("password", None)
            )
        except HTTPException as e:
            print(f"Stream creation failed: {e.detail} for keywords {stream_config.get('keywords')}")
            continue  # Skip this configuration

        # Extract the topic
        topic = stream.data_stream_id

        print(f"Stream created: {topic}")

        # Step 2: Consume messages from the Kafka topic
        print("\nConsuming messages from the Kafka topic...")
        consumer = streaming.consume_kafka_messages(topic)

        try:
            start_time = time.time()
            while True:
                if time.time() - start_time > 180:
                    print("Timeout reached while waiting for messages.")
                    break

                if not consumer.dataframe.empty:
                    print("Dataframe received:")
                    print(consumer.dataframe.head())
                    break

                await asyncio.sleep(1)
        finally:
            # Stop the consumer
            print("\nStopping the Kafka consumer...")
            if consumer:
                consumer.stop()


        # Step 3: Delete the created Kafka stream
        print("\nDeleting the Kafka stream...")

        try:
            response = await streaming.delete_stream(stream)
            print(f"{response["message"]}")
        except Exception as e:
            print(f"Error deleting stream {topic}: {e}")
        
        time.sleep(10) # Wait some seconds to let the consumer clear its data


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(level=logging.INFO)
    pytest.main(["-s", __file__])
