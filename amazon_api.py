from amazon_paapi import AmazonApi
from typing import Optional

from config import AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY

# Initialize the Amazon API client once
amazon = AmazonApi(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG, AMAZON_COUNTRY)

def get_product_info(asin: str) -> Optional[dict]:
    try:
        response = amazon.get_items(asin)

        if not response.items_result or not response.items_result.items:
            return None

        item = response.items_result.items[0]

        return {
            "asin": asin,
            "title": item.item_info.title.display_value,
            "image": item.images.primary.large.url,
            "price": item.offers.listings[0].price.display_amount if item.offers and item.offers.listings else None,
            "url": item.detail_page_url,
            "features": item.item_info.features.display_values if item.item_info.features else []
        }

    except Exception as e:
        print(f"❌ Error fetching product info from Amazon PA API: {e}")
        return None

"""
from amazon_api import get_product_info

data = get_product_info("B0CRCG7816")
if data:
    print(data["title"])
    print(data["price"])
"""