from prometheus_client import start_http_server, Gauge
from dotenv import load_dotenv
import requests
import datetime, time
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
    SLEEP_TIME_SECOND = int(os.getenv("SLEEP_TIME_SECOND", "15"))
    
    data = get_payload()
    for item in data:

        t_start = datetime.datetime.now()

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

            print(f"SUCCESS => SLEEP_TIME_SECOND: {SLEEP_TIME_SECOND}, SERVICE_NAME: {item['service_name']}, METHOD: {item['method']}, STATUS: {response.status_code}")
            status = f"{response.status_code}"
            total_seconds = response.elapsed.total_seconds()

        except requests.exceptions.RequestException as e:
            t_end = datetime.datetime.now()
            duration = t_end - t_start
            total_seconds = round(duration.total_seconds())
            status = f"500"
            print(f"ERROR => SLEEP_TIME_SECOND: {SLEEP_TIME_SECOND}, SERVICE_NAME: {item['service_name']}, METHOD: {item['method']}, STATUS: {500}")


        c.labels(item['service_name'], item['method'], url, status).set(total_seconds)
    
    time.sleep(SLEEP_TIME_SECOND)

if __name__ == "__main__":
    start_http_server(8000)
    print("START SERVICE PORT 8000")
    while True:
        process_request()
        time.sleep(1) 