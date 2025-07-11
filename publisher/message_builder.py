import re

# Message builder

def build_telegram_message(data: dict) -> str:
    """
    Construye un mensaje bonito a partir del JSON generado por el parser
    Espera claves: title, description, price, product_url, savings_percent
    """
    title = clean_telegram_html(data.get("title", "Oferta destacada"))
    description = clean_telegram_html(data.get("content", ""))
    more_info = clean_telegram_html(data.get("more_info", ""))
    offer_price = data.get("offer_price", "")
    normal_price = data.get("normal_price", "")
    savings = data.get("savings_percent")
    url = data.get("product_url", "")
    category = data.get("category", "")
    coupon = data.get("coupon", "")

    message = f"""
<b>🛍 {title}</b>

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
        message += f"❌ <b>Antes:</b> {normal_price}€\n"

    if coupon:
        message += f"""
🏷️ <b><u>CUPÓN:</u></b> {coupon}€\n
"""

    if savings:
        message += f"<b>🔥 Ahorra:</b> {savings}%\n"

    message += f"\n👉 <a href=\"{url}\">¡Lo quiero!</a>"
    return message.strip()

def build_instagram_message(data: dict) -> str:
    """
    Construye un pie de foto para Instagram a partir del JSON generado por el parser.
    Limita el formato a texto plano, con emojis y saltos de línea.
    """
    title = data.get("title", "Oferta destacada")
    description = data.get("content", "")
    more_info = data.get("more_info", "")
    offer_price = data.get("offer_price", "")
    normal_price = data.get("normal_price", "")
    savings = data.get("savings_percent")
    url = data.get("product_url", "")
    category = data.get("category", "")
    coupon = data.get("coupon", "")

    lines = [
        f"🛍 {title}",
        "",
        f"{description}"
    ]

    if more_info:
        lines.append("")
        lines.append(f"ℹ️ {more_info}")

    if offer_price:
        lines.append("")
        lines.append(f"💸 Nuevo Precio: {offer_price}€")

    if normal_price:
        lines.append(f"❌ Antes: {normal_price}€")

    if coupon:
        lines.append(f"🏷️ CUPÓN: {coupon}")

    if savings:
        lines.append(f"🔥 Ahorra: {savings}%")

    if url:
        lines.append("")
        lines.append(f"👉 Ir a la oferta: {url}")

    # Hashtags
    hashtags = ["#oferta", "#descuento", "#ahorro", "#chollo", "#DonOFERTON"]
    if category:
        hashtags.append(f"#{category.lower()}")
    
    lines.append("")
    lines.append(" ".join(hashtags))

    return "\n".join(lines).strip()

def clean_telegram_html(text: str) -> str:
    if not text:
        return ""
    # Eliminar etiquetas HTML no permitidas
    allowed = ['b', 'i', 'u', 's', 'del', 'a', 'code', 'pre']
    return re.sub(r'</?(?!(' + '|'.join(allowed) + r'))[^>]+>', '', text)