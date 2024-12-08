import os  # need this for popen
import time  # for sleep

import requests
import threading
import json

# Output file
OUTPUT_FILE = "predictions.txt"


def download_documents():

    couchdb_url = "http://192.168.5.34:31367/images/_all_docs?include_docs=true"
    username = "admin"  # CouchDB admin username
    password = "password"  # CouchDB admin password

    try:
        response = requests.get(
            couchdb_url,
            headers={"Content-Type": "application/json"},
            auth=(username, password),
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching documents: {e}")
        return

        # Open the output file
    with open(OUTPUT_FILE, "w") as file:
        # Iterate over all rows (documents)
        for row in data.get("rows", []):
            doc = row.get("doc")
            if doc:
                # Extract "predicted_class" and "label" if they exist
                producer_id = doc.get("ProducerID", "N/A")
                predicted_class = doc.get("predicted_class", "N/A")
                label = doc.get("label", "N/A")
                # Write to the file in the desired format
                file.write(f"{producer_id} {predicted_class} {label}\n")

    print(f"Downloaded {len(data.get('rows', []))} documents to {OUTPUT_FILE}")
    file.close()


def main():
    download_documents()


main()
