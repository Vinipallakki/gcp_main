from google.cloud import pubsub_v1
import time
import json
import random

project_id = "databricks-vini"
topic_id = "real-time-data"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

def get_random_data():
    data = {
        "sensor_id": random.randint(1, 500),
        "temperature": random.uniform(20.0, 30.0),
        "humidity": random.uniform(30.0, 60.0),
        "timestamp": time.time()
    }
    return json.dumps(data)

while True:
    data = get_random_data()
    print(f"Publishing data: {data}")  # Print the data to the console
    publisher.publish(topic_path, data.encode("utf-8"))
    time.sleep(0.5)
