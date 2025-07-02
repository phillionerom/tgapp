import asyncio
import random

from db.db import get_unpublished_messages, mark_as_posted
from publisher.channel_config import get_channels_for_category
from publisher.bot_client import send_post


async def publish_messages():
    while True:
        messages = get_unpublished_messages()
        print(f"🔎 {len(messages)} messages to publish.")

        for msg in messages:
            channels = get_channels_for_category(msg["category"])
            for channel in channels:
                delay = random.uniform(2, 5)
                print(f"🕒 Waiting {delay:.2f}s before posting message {msg['id']} to {channel}")
                await asyncio.sleep(delay)

                success = await send_post(channel, msg)
                if success:
                    print(f"✅ Posted message {msg['id']} to {channel}")
                else:
                    print(f"❌ Failed to post message {msg['id']} to {channel}")

            # Solo marcamos como publicado si fue procesado por todos los canales
            mark_as_posted(msg["id"])

        await asyncio.sleep(10)  # wait before checking for new messages


if __name__ == "__main__":
    asyncio.run(publish_messages())