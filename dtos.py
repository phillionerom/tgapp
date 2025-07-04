from dataclasses import dataclass
from typing import Optional


@dataclass
class ProductVendorData:
    offer_price: Optional[float]
    normal_price: Optional[float]
    product_url: Optional[str]
    vendor: Optional[str]
    savings_percent: Optional[float] = None
    title: Optional[str] = None
    product_code: Optional[str] = None
    more_info: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    coupon: Optional[str] = None

    def to_dict(self) -> dict:
        return self.__dict__

