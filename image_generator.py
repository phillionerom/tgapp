import os

from PIL import Image, ImageDraw, ImageFont


def generate_product_image(
    base_path: str,
    product_image_path: str,
    output_path: str,
    title: str,
    price: str,
    old_price: str,
    vendor: str
):
    print("🔧 Generating product image...")

    # fallback
    if product_image_path is None:
        product_image_path = 'assets/not-found-product.png'

    # Load background
    base = Image.open(base_path).convert("RGBA")
    draw = ImageDraw.Draw(base)

    # Load and resize product image
    product_img = Image.open(product_image_path).convert("RGBA")
    max_width = base.width - 100
    max_height = int(base.height * 0.6)  # 60% of height for white area
    product_img.thumbnail((max_width, max_height))

    # Position: centered horizontally, vertically in top (white) zone
    px = (base.width - product_img.width) // 2
    py = 30  # Top padding
    base.paste(product_img, (px, py), product_img)

    # Load fonts
    try:
        font_title = ImageFont.truetype(get_font_path(), 28)
        font_price = ImageFont.truetype(get_font_path(), 50)  # más grande
    except IOError:
        font_title = ImageFont.load_default()
        font_price = ImageFont.load_default()

    # Optional: Draw title below image (if needed)
    # draw.text((40, py + product_img.height + 20), title[:80], fill="black", font=font_title)

    # Draw price in bottom bar (centered, white, bold)
    text_price = f" {price} €"
    bbox = draw.textbbox((0, 0), text_price, font=font_price)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    px_price = (base.width - text_w) // 2
    py_price = base.height - text_h - 30
    #draw.text((px_price, py_price), text_price, fill="white", font=font_price)
    # Draw shadow (desplazada ligeramente)
    shadow_offset = 2
    draw.text((px_price + shadow_offset, py_price + shadow_offset), text_price, fill=(75, 75, 75), font=font_price)

    # Draw main text encima (blanco)
    draw.text((px_price, py_price), text_price, fill="lightgreen", font=font_price)

    # Emoji como imagen
    emoji_path = "assets/emoji/emoji_money_face.png"
    emoji = Image.open(emoji_path).convert("RGBA")
    emoji = emoji.resize((40, 40), resample=Image.LANCZOS)

    # Posición: antes del texto del precio
    emoji_x = px_price - 50  # mueve hacia la izquierda respecto al texto
    emoji_y = py_price + 10
    base.paste(emoji, (emoji_x, emoji_y), emoji)

    if old_price not in [None, "", "None"]:
        # - Old Price
        # Precio anterior (más pequeño y tachado)
        old_price_text = f"Antes: {old_price} €"

        # Fuente más pequeña
        font_previous = ImageFont.truetype(get_font_path(), 26) if os.path.exists(get_font_path()) else ImageFont.load_default()

        # Medidas y posición
        bbox_prev = draw.textbbox((0, 0), old_price_text, font=font_previous)
        text_w_prev = bbox_prev[2] - bbox_prev[0]
        text_h_prev = bbox_prev[3] - bbox_prev[1]
        px_prev = (base.width - text_w_prev) // 2
        py_prev = py_price - text_h_prev - 20  # Un poco encima del precio actual

        # Dibuja el texto gris
        draw.text((px_prev, py_prev), old_price_text, fill="gray", font=font_previous)

        # Dibuja línea tachando el texto (más abajo para cruzar bien)
        #line_y = py_prev + int(text_h_prev * 0.65)
        line_y = py_prev + text_h_prev - 2
        draw.line((px_prev, line_y, px_prev + text_w_prev, line_y), fill="red", width=2)

        # - Savings
        price_float = float(price.replace(",", "."))
        old_price_float = float(old_price.replace(",", "."))
        savings_percent = round((1 - price_float / old_price_float) * 100)

        # Badge content
        badge_title = " ¡Ahorra un"
        badge_percent = f" {savings_percent}% !"

        # Badge styling
        badge_w = 130
        badge_h = 70
        badge_radius = 12
        badge_bg = (220, 20, 60, 270)  # rojo oscuro
        badge_text_color = "white"
        font_badge_title = ImageFont.truetype(get_font_path(), 20)
        font_badge_percent = ImageFont.truetype(get_font_path(), 30)

        # Position to the right of price
        badge_x = px_price + text_w + 30
        badge_y = py_price - 10

        # Draw badge background with rounded corners
        draw.rounded_rectangle(
            (badge_x, badge_y, badge_x + badge_w, badge_y + badge_h),
            radius=badge_radius,
            fill=badge_bg
        )

        # Draw "Ahorra"
        draw.text(
            (badge_x + 15, badge_y + 8),
            badge_title,
            font=font_badge_title,
            fill=badge_text_color
        )

        # Draw savings percentage
        draw.text(
            (badge_x + 15, badge_y + 35),
            badge_percent,
            font=font_badge_percent,
            fill=badge_text_color
        )

    # Vendor
    if vendor == 'amazon':
        logo = Image.open("assets/amazon-logo-tr.webp").convert("RGBA")
        #logo.thumbnail((80, 80))  # Ajusta el tamaño deseado -> PEOR CALIDAD
        # Escalar con máxima calidad
        target_size = (80, 80)
        logo = logo.resize(target_size, resample=Image.LANCZOS)  # mejor calidad

        # Position: top-right, sin margen superior
        padding_right = 33
        lx = base.width - logo.width - padding_right
        ly = 0  # arriba del todo

        base.paste(logo, (lx, ly), logo)  # mantiene transparencia

    # Channel logo
    logo = Image.open("assets/DonOferton-circle-logo.png").convert("RGBA")
    channel_logo_target_size = (80, 80)
    logo = logo.resize(channel_logo_target_size, resample=Image.LANCZOS)  # Ajusta el tamaño a tu gusto

    # Posición del logo: esquina superior izquierda con margen
    margin = 20
    base.paste(logo, (margin, margin), logo)

    # Save final image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base.convert("RGB").save(output_path, format="JPEG", quality=100)

    print(f"✅ Image saved to {output_path}")

    return output_path


def get_font_path():
    path = os.path.join("fonts", "Roboto-Bold.ttf")
    if not os.path.exists(path):
        raise FileNotFoundError(f"⚠️ Fuente no encontrada en {path}")
    return path