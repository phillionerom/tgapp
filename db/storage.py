import json
from pathlib import Path

from db.db import save_message as save_message_db

from config import STORE_DATA


def save_message(new_msg: dict):
    if STORE_DATA == "DB":
        return save_message_db(new_msg)
    elif STORE_DATA == "FILE":
        return save_message_file(new_msg)
    
    print(f"Unsupported store data target: {STORE_DATA}")
    return False

def save_message_file(new_msg: dict):
    data = load_existing_messages_file(new_msg.get("channel"))

    existing_ids = {(msg["channel"], msg["id"]) for msg in data if "id" in msg and "channel" in msg}
    msg_key = (new_msg.get("channel"), new_msg.get("id"))

    output_file = get_message_file(new_msg.get("channel"))

    if msg_key in existing_ids:
        return False  # Duplicate — do not save

    data.append(new_msg)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return True

def load_existing_messages_file(channel):
    output_file = get_message_file(channel)

    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def get_message_file(channel: str):
    return Path(f"messages-{channel}.json")
