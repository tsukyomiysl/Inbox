import requests
import time
def send_message():
    json = {
        "event_id" : input(),
        "event_type" :  input(),
        "event_data" : {"data" : input()
        }
    }
    try:
        response = requests.post("http://127.0.0.1:8000/receive", json=json, timeout=10)
        result = response.status_code
        if result == 202:
            while True:
                response1 = requests.get(f"http://127.0.0.1:8000/events/{json['event_id']}",timeout=10)
                message = response1.json()
                if message["event_status"] == "retry":
                    continue
                elif message["event_status"] == "delivered":
                    print("Event delivered")
                    print(message)
                    break
                elif message["event_status"] == "failed":
                    print("Event delivery failed")
                    print(message)
                    break
                time.sleep(0.8)
        else:
            print(result)
    except requests.exceptions.ConnectionError:
        print("Could not connect to the Webhook Inbox")



send_message()
