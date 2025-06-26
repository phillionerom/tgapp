from telethon import TelegramClient, Button

#from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

#client = TelegramClient(session_name, TELEGRAM_API_ID, TELEGRAM_API_HASH)


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

def build_promotional_message(data: dict) -> str:
    """
    Construye un mensaje bonito a partir del JSON generado por el parser
    Espera claves: title, description, price, product_url, savings_percent
    """
    title = data.get("title", "Oferta destacada")
    description = data.get("content", "")
    more_info = data.get("more_info", "")
    offer_price = data.get("offer_price", "")
    normal_price = data.get("normal_price", "")
    savings = data.get("savings_percent")
    url = data.get("product_url", "")
    category = data.get("category", "")

    message = f"""
<span style'text-size: 50px'><b>🛍 {title}</b></span>

{description}
"""
    
    if more_info:
        message += f"""
ℹ️ {more_info}
"""

    if category:
        message += f"""
#{category}
"""

    message += f"""
<b>💸 Nuevo Precio:</b> {offer_price}€
"""
    
    if normal_price:
        message += f"<b>❌ Antes:</b> {normal_price}€\n"

    if savings:
        message += f"<b>🔥 Ahorro:</b> {savings}%\n"

    message += f"\n👉 <a href=\"{url}\">Ir a la Oferta</a>"
    return message.strip()


# Ejemplo de uso manual (puedes comentar esto si lo integras en otro lado)
# if __name__ == "__main__":
#     example_data = {
#         "title": "Gafas de sol Bugatti",
#         "description": "Diseño elegante y protección UV. Un clásico atemporal.",
#         "price": "20.76",
#         "product_url": "https://www.amazon.es/dp/B0CZS22CNW",
#         "savings_percent": 35.0,
#         "image_url": "https://m.media-amazon.com/images/I/61h5vUO2cdL._AC_SY450_.jpg"
#     }
#     msg = build_promotional_message(example_data)
#     asyncio.run(send_to_channel("@micanalchollos", msg, example_data["image_url"]))
