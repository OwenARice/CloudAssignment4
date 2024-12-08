from kafka import KafkaConsumer, KafkaProducer
import requests
import json
import numpy as np
from PIL import Image
import io
import time

# Kafka configuration
BROKER_IP = "kafka:9092"
TOPIC_INPUT = "images"
TOPIC_OUTPUT = "results"

# CouchDB configuration
COUCHDB_URL = "http://admin:password@192.168.5.34:31367/images"

# Kafka consumer and producer setup
consumer = KafkaConsumer(
    TOPIC_INPUT,
    bootstrap_servers=[BROKER_IP],
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

producer = KafkaProducer(
    bootstrap_servers=[BROKER_IP],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)


def update_couchdb(image_id, predicted_class):
    doc_url = f"{COUCHDB_URL}/{image_id}"
    response = requests.get(doc_url)

    if response.status_code == 200:
        doc = response.json()
        doc["predicted_class"] = predicted_class
        headers = {"Content-Type": "application/json"}
        update_response = requests.put(
            f"{doc_url}?rev={doc['_rev']}", headers=headers, data=json.dumps(doc)
        )

        if update_response.status_code == 201:
            print(f"Document {image_id} successfully updated.")
        else:
            print(
                f"Failed to update document {image_id}. Error: {update_response.text}"
            )
    else:
        print(f"Failed to retrieve document {image_id}. Error: {response.text}")


def process_image_for_inference(image_data):
    img_array = np.array(image_data, dtype=np.uint8).reshape(32, 32, 3)
    image = Image.fromarray(img_array)

    image_buffer = io.BytesIO()
    image.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    return image_buffer


def send_for_inference(image_id, image_data):
    image_buffer = process_image_for_inference(image_data)
    response = requests.post(
        "http://10.244.2.42:5000/infer",
        files={"file": ("image.png", image_buffer, "image/png")},
    )

    if response.status_code == 200:
        predicted_class = response.json()["predicted_class"]
        print(f"Inference result: {image_id} => {predicted_class}")
        obj = {"ID": image_id, "predicted_class": predicted_class}
        producer.send(TOPIC_OUTPUT, value=obj)
        update_couchdb(image_id, predicted_class)
    else:
        print(f"Failed inference for {image_id}. Error: {response.text}")


for message in consumer:
    image_id = message.value["ID"]
    image_data = message.value["data"]
    start_time = time.time()

    send_for_inference(image_id, image_data)

    end_time = time.time()
    print(f"End-to-end latency for {image_id}: {end_time - start_time} seconds")
