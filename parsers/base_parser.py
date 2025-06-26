from abc import ABC, abstractmethod
from telethon.types import Message

from image_generator import generate_product_image

class BaseParser(ABC):
    channel: str  # each parser must define this
    
    @abstractmethod
    def parse(self, message: Message) -> dict | None:
        """
        Parse a Telegram message and return a dict with common fields, or None if it's not relevant.
        Expected output fields:
            - id (int)
            - date (str)
            - channel (str)
            - title (str)
            - content (str)
            - url (optional, str)
        """
        pass

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
