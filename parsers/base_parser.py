import re

import amazon_service
import aliexpress_service

from abc import ABC, abstractmethod
from telethon.types import Message

from image_generator import generate_product_image
from db.db import message_exists
from parsers.parsed_result import ParsedResult
from text_generation import generate
from dtos import ProductVendorData

from .utils import (
    extract_first_url, 
    resolve_redirect_url, 
    detect_store_from_url
)


class BaseParser(ABC):
    channel: str  # each parser must define this
    
    async def parse(self, message: Message) -> ParsedResult | None:
        """
        Parse a Telegram message and return a dict with common fields, or None if it's not relevant.
        Expected output fields:
            - id (int)
            - date (str)
            - channel (str) 
            - title (str)
            - content (str)
            - url (optional, str)
            ...
        """
        if self.skipMessage(message, self.channel):
            return None

        if not message.text:
            return None
        
        # check offer is still alive
        if self.isOutOfStock(message.text):
            print(f"👎 Message seems is finished offer: {message.text} \n\n> Will ignore it...")
            return None

        text = message.text.strip()
        if "€" not in text:
            return None  # Not a deal post
        
        self.logParseStart(message, self.channel)

        product_short_url = extract_first_url(text)
        product_source_url = resolve_redirect_url(product_short_url)

        vendor_product: ProductVendorData = None

        vendor = detect_store_from_url(product_source_url)

        print(f"🌐 Trying to get product page: [{product_source_url}]")

        if vendor == 'amazon':
            vendor_product = await amazon_service.get_product(message.id, self.channel, product_source_url)
        elif vendor == 'aliexpress':
            vendor_product = await aliexpress_service.get_product(message.id, self.channel, product_source_url)
        else:
            # For now only amazon vendor is supported
            print(f"\n*** Found Vendor not supported: \"{vendor}\" in channel: {self.channel}")
            return None
        
        if self.validateVendorProduct(vendor_product, vendor) is None:
            return None
        
        ai_data = generate(text)

        print(f"AI DATA={ai_data}")
        
        try:
            generated_image = self.generateProductImage(message.id, ai_data, vendor, vendor_product.image_url)
        except Exception as e:
            print(f"[ERROR] Failed to generate image: {e}")
            generated_image = None

        return ParsedResult(
            message_id=message.id,
            date=message.date,
            channel=self.channel,
            title=ai_data['title'], 
            content=ai_data['description'],
            more_info=ai_data['more_info'], 
            offer_price=vendor_product.offer_price if ai_data['price'] in [None, ''] else ai_data['price'],
            normal_price=vendor_product.normal_price if ai_data['old_price'] in [None, ''] else ai_data['old_price'],
            savings_percent=vendor_product.savings_percent,
            message_url=f"https://t.me/{self.channel}/{message.id}",
            short_url=product_short_url,
            product_code=vendor_product.product_code,
            product_url=vendor_product.product_url,
            image=generated_image if generated_image else vendor_product.image_url, # fallback amz image
            category=vendor_product.category,
            coupon=ai_data['coupon'],
            vendor=vendor
        )

    def generateProductImage(self, id, data, vendor, product_image_url):
        print(f"GenerateProductImage data={data} img url={product_image_url}")
        return generate_product_image(
            base_path="assets/BaseProd-v2.png",
            product_image_path=product_image_url,
            output_path=f"output/{self.channel}-{id}_composed.jpg",
            title=data['title'],
            price=f"{data['price']}",
            old_price=f"{data['old_price']}", # de momento guardo sólo el old_price, poner descuento o calcularlo
            vendor=vendor
        )
    
    def validateVendorProduct(self, vendor_product: ProductVendorData, vendor) -> ProductVendorData:
        if vendor_product is None:
            print(f"❗ Unable to get vendor product data from \"{vendor}\" product")
            return None
        
        return vendor_product
    
    def skipMessage(self, message, channel):
        exists = message_exists(message.id, channel)
        
        if exists:
            print(f"⏩ - Skipping message id {message.id} from `{channel}`. Already exists...")
        
        return exists
    
    def logParseStart(self, message, channel):
        print(f"-------------------------------------------------------------------------------\n")
        print(f"📟 Starting to parse new message in `{channel}`... Message id={message.id}")


    def isOutOfStock(self, text: str) -> bool:
        text = text.lower()

        patterns = [
            r"\bagotad[oa]\b",                              # "agotado" o "agotada"
            r"oferta\s+agotada",                            # "oferta agotada"
            r"precio\s+agotado",                            # "precio agotado"
            r"✅\s*precio\s+agotado",                       # ✅ PRECIO AGOTADO
            r"🚨.*agotad[oa]",                              # 🚨 OFERTA AGOTADA
        ]

        return any(re.search(p, text) for p in patterns)