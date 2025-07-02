
from parsers.utils import (
    replace_amazon_affiliate_tag, 
    extract_asin_from_url,
    download_image_from_url
)
from amazon_api import get_product_info
from amazon_scraper import get_amazon_main_image_by_bs4, get_amazon_main_image, get_amazon_product_data


async def get_product(message_id, channel, source_url):
    vendor_product = await get_amazon_product_data(source_url)

    if vendor_product['ok']:
        #print(f"amz img path={vendor_product['image_url']}")
        print(f"amz current_price={vendor_product['current_price']}")
        print(f"amz original_price={vendor_product['original_price']}")
        print(f"amz savings_percent={vendor_product['savings_percent']}")
        print(f"amz category={vendor_product['category']}")

        product_image = await download_image_from_url(vendor_product['image_url'], f"images/amazon/{channel}-{message_id}_product.jpg")

        asin = extract_asin_from_url(source_url)
        my_product_url = replace_amazon_affiliate_tag(source_url) if source_url else None

        vendor_product['product_code'] = asin
        vendor_product['my_product_url'] = my_product_url
        vendor_product['product_image'] = product_image

        # data = get_product_info(asin)
        # if data:
        #     print(data["title"])
        #     print(data["price"])

        #     amz_img_path = await client.download_media(data["image"], file=f"images/amazon/{message.id}-{self.channel}-{asin}.jpg")

        return vendor_product
    
    return None