from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ParsedResult:
    message_id: int
    date: datetime
    channel: str
    title: str
    content: str
    more_info: Optional[str]
    offer_price: Optional[float]
    normal_price: Optional[float]
    savings_percent: Optional[float]
    message_url: str
    short_url: Optional[str]
    product_code: Optional[str]
    product_url: Optional[str]
    image: Optional[str]
    category: Optional[str]
    vendor: Optional[str]

    def to_dict(self) -> dict:
        return self.__dict__
