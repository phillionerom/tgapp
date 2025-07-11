import asyncio
import random

from db.db import get_unpublished_messages, mark_as_posted
from db.models import ParsedMessage

from publisher.publisher_rules import get_publication_targets

from publisher.publisher_telegram import publish as publish_telegram
from publisher.publisher_instagram import publish as publish_instagram


async def publish_messages():
    while True:
        messages = get_unpublished_messages()
        
        log_status(messages)

        for msg in messages:
            targets = get_publication_targets(msg["category"])
            telegram_channels = targets.get("telegram_channels", [])
            instagram_enabled = targets.get("instagram", False)
            facebook_enabled = targets.get("facebook", False)
            web_enabled = targets.get("web", False)

            success_count = 0
            total_targets = len(telegram_channels) + instagram_enabled + facebook_enabled + web_enabled

            # Telegram
            for channel in telegram_channels:
                delay = random.uniform(2, 5)
                print(f"🕒 Waiting {delay:.2f}s before posting message {msg['id']} to {channel}")
                await asyncio.sleep(delay)

                success = await publish_telegram(channel, msg)
                if success:
                    print(f"✅ Posted message {msg['id']} to {channel}\n")
                    success_count += 1
                else:
                    print(f"❌ Failed to post message {msg['id']} to {channel}\n")

            if instagram_enabled:
                print(f"\n📸 [Placeholder] Would post to Instagram: {msg['id']}")
                delay = random.uniform(2, 5)
                print(f"🕒 Waiting {delay:.2f}s before posting message {msg['id']} to Instagram")
                await asyncio.sleep(delay)
                if publish_instagram(msg):
                    success_count += 1
            if facebook_enabled:
                print(f"📘 [Placeholder] Would post to Facebook: {msg['id']}")
                success_count += 1
            if web_enabled:
                print(f"🌐 [Placeholder] Would post to Web: {msg['id']}")
                success_count += 1

            # Solo marcamos como publicado si se publicó en todos los destinos
            if success_count == total_targets:
                mark_as_posted(msg["id"])
                print(f"✅✅ Fully posted message {msg['id']}")
            else:
                print(f"⚠️ Message {msg['id']} not fully posted")

        await asyncio.sleep(10)

def log_status(messages_found):
    amount = len(messages_found)
    if amount > 0:
        print(f"🔎 {amount} messages to publish.")
    else:
        print(f"🔎 There aren't messages to publish... let's wait...")


if __name__ == "__main__":
    asyncio.run(publish_messages())