from telethon import Button

from publisher.message_builder import build_promotional_message

#
# This send message via user, not by bot
#
async def send_to_channel(client, channel_username: str, message, image_url: str | None = None):
    await client.start()

    print(f"LLEGA PARA SEND={message}")

    msg = build_promotional_message(message)

    print(f"MENSAJE CONSTRUIDO={msg}")

    if message['image']:
        await client.send_file(
            entity=channel_username,
            file=message['image'],
            caption=msg,
            buttons=[Button.url("🔗 Ir a la Oferta", message['product_url'])],
            parse_mode="html"
        )
    else:
        await client.send_message(
            entity=channel_username,
            message=msg,
            buttons=[Button.url("🔗 Ir a la Oferta", message['product_url'])],
            parse_mode="html"
        )
    print(f"✅ Mensaje enviado a {channel_username}")
    await client.disconnect()