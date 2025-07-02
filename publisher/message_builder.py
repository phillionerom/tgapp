import re

# Message builder

def build_promotional_message(data: dict) -> str:
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
        message += f"<b>❌ Antes:</b> {normal_price}€\n"

    if savings:
        message += f"<b>🔥 Ahorra:</b> {savings}%\n"

    message += f"\n👉 <a href=\"{url}\">¡Lo quiero!</a>"
    return message.strip()

def clean_telegram_html(text: str) -> str:
    if not text:
        return ""
    # Eliminar etiquetas HTML no permitidas
    allowed = ['b', 'i', 'u', 's', 'del', 'a', 'code', 'pre']
    return re.sub(r'</?(?!(' + '|'.join(allowed) + r'))[^>]+>', '', text)