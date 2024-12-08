#
#
# Author: Aniruddha Gokhale
# CS4287-5287: Principles of Cloud Computing, Vanderbilt University
#
# Created: Sept 6, 2020
#
# Purpose:
#
#    Demonstrate the use of Kafka Python streaming APIs.
#    In this example, demonstrate Kafka streaming API to build a consumer.
#

import os  # need this for popen
import time  # for sleep
from kafka import KafkaConsumer  # consumer of events

import requests
import threading
import json


# Fire up the kafka images consumer as a function
def image_consumer():

    # We can make this more sophisticated/elegant but for now it is just
    # hardcoded to the setup I have on my local VMs

    # acquire the consumer
    # (you will need to change this to your bootstrap server's IP addr)
    consumer = KafkaConsumer(bootstrap_servers="kafka:9092")

    # subscribe to topic
    consumer.subscribe(topics=["images"])

    couchdb_url = "http://192.168.5.34:31367/images"
    username = "admin"  # CouchDB admin username
    password = "password"  # CouchDB admin password

    # we keep reading and printing
    for msg in consumer:

        data = json.loads(msg.value)

        post_url = couchdb_url + "/" + data["ID"]

        response = requests.put(
            post_url,
            headers={"Content-Type": "application/json"},
            auth=(username, password),
            data=json.dumps(data),
        )

        if response.status_code == 201:
            print("Document added successfully:", response.json())
        else:
            print("Failed to add document:", response.status_code, response.text)

    # we are done. As such, we are not going to get here as the above loop
    # is a forever loop.
    consumer.close()


# Listen for the results/predictions and update the item in the DB
def results_consumer():

    # acquire the consumer
    # (you will need to change this to your bootstrap server's IP addr)
    consumer = KafkaConsumer(bootstrap_servers="kafka:9092")

    # subscribe to topic
    consumer.subscribe(topics=["results"])

    couchdb_url = "http://192.168.5.34:31367/images"
    username = "admin"  # CouchDB admin username
    password = "password"  # CouchDB admin password

    # we keep reading and printing
    for msg in consumer:

        data = json.loads(msg.value)

        post_url = couchdb_url + "/" + data["ID"]

        response = requests.put(
            post_url,
            headers={"Content-Type": "application/json"},
            auth=(username, password),
            data=json.dumps(data),
        )

        if response.status_code == 201:
            print("Document updated successfully:", response.json())
        else:
            print("Failed to update document:", response.status_code, response.text)

    # we are done. As such, we are not going to get here as the above loop
    # is a forever loop.
    consumer.close()


def main():
    image_thread = threading.Thread(target=image_consumer)
    result_thread = threading.Thread(target=results_consumer)

    image_thread.start()
    result_thread.start()


main()
