from telethon import TelegramClient, events

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION
from db.db import save_message
from parsers.parser_loader import get_parser_for

client = TelegramClient(TELEGRAM_SESSION, TELEGRAM_API_ID, TELEGRAM_API_HASH)

DEFAULT_FETCH_LIMIT = 20 # Previous messages to fetch when process starts


async def fetch_last_messages(channel_username, limit=DEFAULT_FETCH_LIMIT):
    messages = []
    async for msg in client.iter_messages(channel_username, limit=limit):
        messages.append(msg)
    return messages

def listen_to_channel(channel_username, parser_func):
    @client.on(events.NewMessage(chats=channel_username))
    async def handler(event):
        parsed = await parser_func.parse(event.message)
        if parsed:
            save_message(parsed.to_dict())

async def init_all_channels(channels):
    for channel in channels:
        parser = get_parser_for(channel)
        if not parser:
            print(f"⚠️ No parser found for channel: {channel}. Skipping.\n")
            continue

        print(f"\n📥 >>> Fetching last messages from: {channel}\n")

        try:
            messages = await fetch_last_messages(channel)
        except Exception as e:
            print(f"[ERROR] Failed to fetch messages from {channel}: {e}")
            continue

        for msg in reversed(messages):
            try:
                parsed = await parser.parse(msg)
                if parsed:
                    save_message(parsed.to_dict())
                    print(f"✅ Stored message {msg.id} from {channel}")
                else:
                    print(f"⏩ --- Skipped message {msg.id} (not relevant) in {channel}")
            except Exception as e:
                print(f"[ERROR] Failed to parse message {msg.id} in {channel}: {e}")

        # Register listener
        try:
            listen_to_channel(channel, parser)
            print(f"🎧 Listening to new messages in {channel}")
        except Exception as e:
            print(f"[ERROR] Could not start listener for {channel}: {e}")

def start_client(channels):
    async def main():
        await init_all_channels(channels)
        print("\n**********************************************\n🟢 Listening for new messages...\n**********************************************\n")
        await client.run_until_disconnected()

    client.start()
    client.loop.run_until_complete(main())
