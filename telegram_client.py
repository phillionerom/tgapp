from telethon import TelegramClient, events
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION
from db import save_message
from parsers import get_parser_for

client = TelegramClient(TELEGRAM_SESSION, TELEGRAM_API_ID, TELEGRAM_API_HASH)


async def fetch_last_messages(channel_username, limit=10):
    messages = []
    async for msg in client.iter_messages(channel_username, limit=limit):
        messages.append(msg)
    return messages

def listen_to_channel(channel_username, parser_func):
    @client.on(events.NewMessage(chats=channel_username))
    async def handler(event):
        parsed = parser_func(event.message)
        if parsed:
            save_message(parsed)

async def init_all_channels(channels):
    for channel in channels:
        parser = get_parser_for(channel)
        print(f"Fetching last messages from: {channel}")
        messages = await fetch_last_messages(channel, limit=10)
        for msg in reversed(messages):
            parsed = parser(msg)
            if parsed:
                save_message(parsed)

        # Register listener for future messages
        listen_to_channel(channel, parser)

def start_client(channels):
    async def main():
        await init_all_channels(channels)
        print("Listening for new messages...")
        await client.run_until_disconnected()

    client.start()
    client.loop.run_until_complete(main())
