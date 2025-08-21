import json


def parse_message(msg):
    try:
        data = json.loads(msg.data.decode())
        return data
    except json.JSONDecodeError:
        print("[NATS] Failed to decode message")
        return {}
