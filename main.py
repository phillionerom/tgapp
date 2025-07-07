import argparse
import asyncio

from telethon import TelegramClient
from telethon.errors import FloodWaitError

from db.storage import save_message
from OLD.realtime_listener import start_listening
from OLD.sender import send_to_channel

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

from parsers.registry import load_parsers
PARSERS = load_parsers()

# === CONFIGURATION ===
session_name = 'reader'
channel = 'Liquidaciones'  # e.g. 'chollometro'
keywords = ['REBAJA', 'descuento']  # Customize as needed
message_limit = 50 # 500  # Adjust the number of messages to fetch

# === TELEGRAM CLIENT ===
client = TelegramClient(session_name, TELEGRAM_API_ID, TELEGRAM_API_HASH)


# === MESSAGE PARSING FUNCTION ===
def message_matches_keywords(message_text: str, keywords: list[str]) -> bool:
    text = message_text.lower()
    #return any(keyword in text for keyword in keywords)
    # disabled for now
    return True

# === SAFE SCRAPING FUNCTION ===
async def fetch_messages(channel_name: str, keywords: list[str], limit: int = message_limit):
    print(f"📥 Fetching last {limit} messages from: {channel_name}")
    try:
        parser = PARSERS.get(channel_name.lower())
        if not parser:
            raise ValueError(f"No parser found for channel '{channel_name}'")

        async for message in client.iter_messages(channel_name, limit=limit):
            if message.text and message_matches_keywords(message.text, keywords):
                parsed = await parser.parse(message, client=client)
                if parsed:
                    print(f"\n🔎 Parsed message:\n{parsed['title']}")
                    if save_message(parsed):
                        my_channel = "@D_o_n_OFERTON"
                        print(">>> MESSAGE SHOULD BE SENT TO MY CHANNEL")
                        await send_to_channel(client, my_channel, parsed)
                else:
                    print("Parsed message from not supported Vendor")
        
            await asyncio.sleep(0.5) # 0.2
    except FloodWaitError as e:
        print(f"⏳ Flood wait. Sleeping {e.seconds}s...")
        await asyncio.sleep(e.seconds)
        await fetch_messages(channel_name, keywords, limit)
    except Exception as e:
        print(f"❌ Error: {e}")


async def main(live_mode: bool):
    await client.start()

    if live_mode:
        print("🟢 Live mode ON – Listening for new messages...")
        await start_listening(client, channel, keywords)
    else:
        print("📄 Static mode – Fetching historical messages...")
        await fetch_messages(channel, keywords, message_limit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram Channel Reader")
    parser.add_argument('--live', action='store_true', help="Activate real-time listening mode")
    args = parser.parse_args()

    with client:
        client.loop.run_until_complete(main(args.live))
