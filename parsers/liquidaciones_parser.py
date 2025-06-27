import re

import amazon_service

from telethon.types import Message

from db.db import message_exists
from .base_parser import BaseParser
from .utils import (
    extract_first_url, 
    resolve_redirect_url, 
    detect_store_from_url
)

from text_generation import generate


class LiquidacionesParser(BaseParser):
    channel = "liquidaciones"

    async def parse(self, message: Message, client=None) -> dict | None:
        if self.skipMessage(message, self.channel):
            return None

        if not message.text:
            return None
        
        # check offer is still alive
        if is_out_of_stock(message.text):
            print(f"Message seems is finished offer: {message.text}")
            return None

        text = message.text.strip()
        if "€" not in text:
            return None  # Not a deal post

        product_short_url = extract_first_url(text)
        product_source_url = resolve_redirect_url(product_short_url)

        vendor_product = None

        vendor = detect_store_from_url(product_source_url)

        if vendor == 'amazon':
            vendor_product = await amazon_service.get_product(message.id, self.channel, product_source_url)
        else:
            # For now only amazon vendor is supported
            print(f"*** Found Vendor not supported: {vendor} in channel: {self.channel}")
            return None

        ai_data = generate(text)

        print(f"AI DATA={ai_data}")
        
        generated_image = self.generateProductImage(message.id, ai_data, vendor, vendor_product['product_image'])

        return {
            "message_id": message.id,
            "date": message.date,
            "channel": self.channel,
            "title": ai_data['title'], 
            "content": ai_data['description'],
            "more_info": ai_data['more_info'], 
            "offer_price": vendor_product['current_price'],
            "normal_price": vendor_product['original_price'] if ai_data['old_price'] is None or ai_data['old_price'] == '' else ai_data['old_price'],
            "savings_percent": vendor_product['savings_percent'],
            "message_url": f"https://t.me/{self.channel}/{message.id}",
            "short_url": product_short_url,
            "product_code": vendor_product['product_code'],
            "product_url": vendor_product['my_product_url'],
            "image": generated_image if generated_image is not None else vendor_product['image_url'], # fallback amz image
            "category": vendor_product['category']
        }

def is_out_of_stock(text: str) -> bool:
    text = text.lower()

    patterns = [
        r"\bagotad[oa]\b",                              # "agotado" o "agotada"
        r"oferta\s+agotada",                            # "oferta agotada"
        r"precio\s+agotado",                            # "precio agotado"
        r"✅\s*precio\s+agotado",                       # ✅ PRECIO AGOTADO
        r"🚨.*agotad[oa]",                              # 🚨 OFERTA AGOTADA
    ]

    return any(re.search(p, text) for p in patterns)