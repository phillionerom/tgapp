def build_promotional_text(message) -> str:
    """
    Construye el texto promocional con formato HTML para publicar en Telegram.
    `message` es un objeto SQLAlchemy (ParsedMessage)
    """
    lines = []

    # ✅ Título destacado
    if message.title:
        lines.append(f"<b>{message.title}</b>")

    # 📝 Descripción
    if message.content:
        lines.append(f"{message.content}")

    # 💸 Precio actual
    if message.offer_price:
        lines.append(f"\n<b>💰 Precio:</b> {message.offer_price} €")

    # 🕹️ Precio anterior (si hay)
    if message.normal_price:
        lines.append(f"<s>Precio antes: {message.normal_price} €</s>")

    # 📉 Ahorro
    if message.savings_percent:
        lines.append(f"<b>🟢 Ahorro: {message.savings_percent}%</b>")

    # 🧭 Categoría
    if message.category:
        lines.append(f"\n📦 Categoría: {message.category}")

    # 🔗 URL
    if message.product_url:
        lines.append(f"\n<a href=\"{message.product_url}\">🛍 Ver Oferta</a>")

    return "\n".join(lines).strip()