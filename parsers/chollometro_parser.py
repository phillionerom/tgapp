from .base_parser import BaseParser
from telethon.types import Message

class ChollometroParser(BaseParser):
    channel = "chollometro"

    def parse(self, message: Message) -> dict | None:
        if not message.text:
            return None

        text = message.text.strip()
        if "€" not in text:
            return None  # Not a deal post

        return {
            "id": message.id,
            "date": str(message.date),
            "channel": self.channel,
            "title": text.split('\n')[0],
            "content": text,
            "url": f"https://t.me/{self.channel}/{message.id}"
        }
