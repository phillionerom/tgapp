# publisher.py
from db import get_unpublished_messages, mark_as_published
from bots import get_bot_for_channel
from utils import convert_message_to_post, get_channels_for_category

def publish():
    messages = get_unpublished_messages()

    for msg in messages:
        categories = msg["categories"]
        for category in categories:
            target_channels = get_channels_for_category(category)
            
            for channel in target_channels:
                bot = get_bot_for_channel(channel)
                post = convert_message_to_post(msg, channel)

                success = bot.send_message(channel, post)
                if success:
                    mark_as_published(msg["id"], channel)

if __name__ == "__main__":
    publish()
