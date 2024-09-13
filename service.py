from prometheus_client import start_http_server, Gauge
from dotenv import load_dotenv
import requests
import datetime, time
import yaml
import os
import re

load_dotenv()

def get_payload():
    file_path = '/app/.data/payload.yaml'
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

c = Gauge('uptime_requests_response_time', 'HTTP Request', [
    'service_name',
    'method', 
    'uri', 
    'status_code',
    'type_validate'
])

def validate_body(type_validate, body, body_to_validate):
    if type_validate == "BODY_REGEX":
        x = re.search(body_to_validate, body)
        try:
            x.span()
            return True	
        except:
            return False
    
    if type_validate == "BODY_EQUAL":
        return body == body_to_validate
    
def validate_status_code(status_code):
    return status_code >= 200 < 400


def process_request():
    SLEEP_TIME_SECOND = int(os.getenv("SLEEP_TIME_SECOND", "15"))
    
    data = get_payload()
    for item in data:
        response_validated = True
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
            
            if "validate_by_body" in item:
                response_validated = validate_body(item['validate_by_body']['type'], response.text, item['validate_by_body']['body_text'])
            else:
                response_validated = validate_status_code(response.status_code)

            print(f"{datetime.datetime.now()} INFO => SLEEP_TIME_SECOND: {SLEEP_TIME_SECOND}, SERVICE_NAME: {item['service_name']}, METHOD: {item['method']}, STATUS: {response.status_code}")
            status = f"{response.status_code}"
            total_seconds = response.elapsed.total_seconds()

        except requests.exceptions.RequestException as e:
            t_end = datetime.datetime.now()
            response_validated = False
            duration = t_end - t_start
            total_seconds = round(duration.total_seconds())
            status = f"500"
            print(f"{datetime.datetime.now()} ERROR => SLEEP_TIME_SECOND: {SLEEP_TIME_SECOND}, SERVICE_NAME: {item['service_name']}, METHOD: {item['method']}, STATUS: {status}")

        c.labels(
            item['service_name'], 
            item['method'], 
            url, 
            status, 
            "success" if response_validated else "error"
        ).set(total_seconds)
    
    time.sleep(SLEEP_TIME_SECOND)

if __name__ == "__main__":
    start_http_server(8000)
    print("START SERVICE PORT 8000")
    while True:
        process_request()
        time.sleep(1) 