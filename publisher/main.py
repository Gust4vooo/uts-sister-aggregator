import requests
import json
import time
import uuid
import random

AGGREGATOR_URL = "http://aggregator:8000/publish"

def generate_event():
    return {
        "topic": random.choice(["user_login", "system_health", "payment_event"]),
        "event_id": str(uuid.uuid4()),
        "source": "publisher_service",
        "payload": {"value": random.randint(1, 100)}
    }

print("🚀 Publisher service started. Waiting for aggregator to be ready...")
time.sleep(10) 

while True:
    try:
        event = generate_event()
        print(f"   -> Sending event: (topic={event['topic']}, id={event['event_id']})")

        response = requests.post(
            AGGREGATOR_URL,
            data=json.dumps(event),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status() 
        print(f"   <- Received response: Status {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error connecting to aggregator: {e}")

    time.sleep(2)