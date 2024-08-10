from prometheus_client import start_http_server, Gauge, Counter, generate_latest
from dotenv import load_dotenv
import requests
import time
import yaml
import os

load_dotenv()

def get_payload():
    file_path = '/app/.data/payload.yaml'
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

c = Gauge('uptime_requests_response_time', 'HTTP Request', [
    'service_name',
    'method', 
    'uri', 
    'status_code'
])

def process_request():
    
    data = get_payload()
    for item in data:
        url = item["url"]
        payload = item["body"]

        headers = item["headers"] 
    
        try:
            if item['method'] == "POST":
                response = requests.post(url, data=payload, headers=headers)
            elif item['method'] == "PUT":
                response = requests.put(url, data=payload, headers=headers)
            else: 
                response = requests.get(url, data=payload, headers=headers)

            status = f"{response.status_code}"
        except requests.exceptions.RequestException as e:
            status = f"500"

        c.labels(item['service_name'], item['method'], url, status).set(response.elapsed.total_seconds())
    
    time.sleep(os.getenv("SLEEP_TIME_SECOND", 15))


if __name__ == "__main__":
    start_http_server(8000)

    while True:
        process_request()
        time.sleep(1) 