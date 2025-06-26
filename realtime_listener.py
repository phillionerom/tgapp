from telethon import events

from storage import save_message

from parsers.registry import load_parsers
PARSERS = load_parsers()

def message_matches_keywords(text: str, keywords: list[str]) -> bool:
    return any(keyword in text.lower() for keyword in keywords)


async def start_listening(client, channel_name: str, keywords: list[str]):

    @client.on(events.NewMessage(chats=channel_name))
    async def handler(event):
        if event.message.text and message_matches_keywords(event.message.text, keywords):
            print("\n📡 New matching message received:")
            print(event.message.text)

            parser = PARSERS.get(channel_name.lower())
            if not parser:
                raise ValueError(f"No parser found for channel '{channel_name}'")
            
            parsed = await parser.parse(event.message, client=client)
            if parsed:
                print(f"\n📡 Parsed live message:\n{parsed['title']}")
                save_message(parsed)

    await client.run_until_disconnected()