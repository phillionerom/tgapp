import httpx
import time
import hashlib
import hmac
import requests

from playwright.async_api import async_playwright
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from aliexpress_sdk import AliExpressSDK

from config import ALIEXPRESS_APP_KEY, ALIEXPRESS_APP_SECRET, ALIEXPRESS_TRACKING_ID
from parsers.utils import download_image_from_url
from dtos import ProductVendorData

aliexpress = AliExpressSDK(ALIEXPRESS_APP_KEY, ALIEXPRESS_APP_SECRET, ALIEXPRESS_TRACKING_ID)


async def get_product(message_id, channel, product_url) -> ProductVendorData:
    final_url = await resolve_aliexpress_redirect(product_url)
    print(f"ALI resolved url={final_url}")

    clean_url = aliexpress.clean_url(final_url)

    #aff_link = aliexpress.generate_affiliate_link(clean_url)

    #print("AliExpress AFF LINK =", aff_link)
    #print("AliExpress CLEAN URL =", clean_url)

    product = await get_aliexpress_product_info(message_id, channel, clean_url)

    return product



async def get_aliexpress_product_info(message_id, channel: str, url: str) -> ProductVendorData | None:
    product_id = extract_product_id(url)
    if not product_id:
        print("[AliExpress] ❌ Could not extract product ID from URL.")
        return None

    method = "aliexpress.affiliate.productdetail.get"
    base_url = "https://api-sg.aliexpress.com/sync"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    params = {
        "method": method,
        "app_key": ALIEXPRESS_APP_KEY,
        "timestamp": timestamp,
        "format": "json",
        "v": "2.0",
        "sign_method": "md5",
        "product_ids": product_id,
        "target_currency": "EUR",
        "target_language": "ES",
    }

    # Generate MD5 sign
    params["sign"] = generate_sign(params, ALIEXPRESS_APP_SECRET)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(base_url, data=params)
            if res.headers.get("Content-Type", "").startswith("application/json"):
                data = res.json()
                #print(f"DATA PRODUCT={data}")
                result = data.get("aliexpress_affiliate_productdetail_get_response", {}).get("resp_result", {}).get("result", {})
                products_obj = result.get("products", {})
                products = products_obj.get("product", [])
                if products:
                    product = products[0]
                    image = product.get("product_main_image_url", "")
                    product_image = await download_image_from_url(image, f"images/aliexpress/{channel}-{message_id}_product.jpg")
                    #live_price = await get_live_price_from_promotion_link(product.get("promotion_link", ""))
                    #print(f"AE precio con PROMO = {live_price}")
                    return ProductVendorData(
                        product_code=product_id,
                        product_url=product.get("product_detail_url", url),
                        title=product.get("product_title", ""),
                        offer_price=product.get("sale_price", ""),
                        normal_price= product.get("original_price", ""),
                        savings_percent=0,  # puedes calcularlo si lo deseas
                        category=product.get("first_level_category_name", ""),
                        image_url=product_image,
                        vendor='aliexpress'
                    )
            else:
                print("[AliExpress API] ❌ Response is not JSON. Falling back to HTML scraping.")
    except Exception as e:
        print(f"[AliExpress API] ❌ Error during request: {e}")

    # Fallback: scrape HTML
    print(f"Trying to download ALIEXPRESS img from={url}")
    image = await get_product_data_from_html(url)
    if image:
        product_image = await download_image_from_url(image, f"images/aliexpress/{channel}-{message_id}_product.jpg")
        return {
            "product_image": product_image,
            "title": "",  # You could scrape more fields if needed
            "current_price": 0,
            "category": "",
            "original_price": 0,
            "savings_percent": 0,
            "my_product_url": url,
            "product_code": product_id
        }

    return None

async def get_live_price_from_promotion_link(promotion_url: str) -> str | None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(promotion_url, timeout=15000)
            await page.wait_for_selector('[class*="product-price"]', timeout=10000)

            # Captura el precio visible
            price_element = await page.query_selector('[class*="product-price"]')
            price_text = await price_element.text_content() if price_element else None

            return price_text.strip() if price_text else None

        except Exception as e:
            print(f"[AliExpress Scraper] ❌ Error al obtener precio desde promoción: {e}")
            return None

        finally:
            await browser.close()

def get_product_main_image(product_id: str, app_key: str, app_secret: str, tracking_id: str):
    method = "api.product.get"
    timestamp = str(int(time.time() * 1000))
    api_path = "openapi/param2/2/portals.open/api.product.get"
    base_url = f"https://api.aliexpress.com/{api_path}/{app_key}"

    params = {
        "app_key": app_key,
        "timestamp": timestamp,
        "sign_method": "hmac-sha256",
        "product_id": product_id,
        "tracking_id": tracking_id,
    }

    # Generar firma
    query = urlencode(sorted(params.items()))
    sign_str = f"{api_path}/{app_key}{query}"
    sign = hmac.new(app_secret.encode(), sign_str.encode(), hashlib.sha256).hexdigest().upper()
    params["sign"] = sign

    # Hacer petición
    res = requests.get(base_url, params=params)
    data = res.json()

    try:
        print(f"MAIN IMAGE DATA={data}")
        return data["result"]["image_url"]
    except Exception as e:
        print(f"[AliExpress API] ❌ Error parsing: {e} | Raw: {data}")
        return None
    
# move to aliexpress_scraper.py
async def get_product_data_from_html(url: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers)
            html = resp.text

        soup = BeautifulSoup(html, "html.parser")

        # Extract product image
        og_image = soup.find("meta", property="og:image")
        image_url = og_image["content"] if og_image else None
        if not image_url:
            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                image_url = img_tag["src"]

        # Extract main category
        breadcrumb_links = soup.find_all("a", href=True)
        categories = [
            a.text.strip()
            for a in breadcrumb_links
            if "/category/" in a["href"] and a.text.strip()
        ]
        main_category = categories[0] if categories else None

        # Extract title
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"].strip() if title_tag else None

        # Extract current price
        current_price_tag = soup.select_one('[class*="product-price-current"]')
        current_price = current_price_tag.text.strip().replace("€", "").replace(",", ".") if current_price_tag else None

        # Extract original/old price
        old_price_tag = soup.select_one('[class*="product-price-original"]')
        original_price = old_price_tag.text.strip().replace("€", "").replace(",", ".") if old_price_tag else None

        # Calculate savings percent
        savings_percent = None
        try:
            if original_price and current_price:
                savings_percent = round(
                    (float(original_price) - float(current_price)) / float(original_price) * 100, 2
                )
        except ValueError:
            pass

        return {
            "image_url": image_url,
            "main_category": main_category,
            "title": title,
            "current_price": current_price,
            "original_price": original_price,
            "savings_percent": savings_percent
        }

    except Exception as e:
        print(f"[ERROR] Failed to get product info: {e}")
        return {
            "image_url": None,
            "main_category": None,
            "title": None,
            "current_price": None,
            "original_price": None,
            "savings_percent": None
        }

async def get_aliexpress_category(url: str) -> str | None:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers)
            soup = BeautifulSoup(resp.text, "html.parser")

            breadcrumb = soup.find_all("a", href=True)
            categories = [
                a.text.strip()
                for a in breadcrumb
                if "/category/" in a["href"] and a.text.strip()
            ]

            # Return last category or full path as you prefer
            if categories:
                return categories[-1]  # more specific
                # return " > ".join(categories)  # full path
            return None
    except Exception as e:
        print(f"[AliExpress Category] ❌ Error: {e}")
        return None

async def resolve_aliexpress_redirect(url: str) -> str | None:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=15000)  # 15s timeout
            final_url = page.url
            await browser.close()
            return final_url
    except Exception as e:
        print(f"[Playwright] ❌ Failed to resolve redirect: {e}")
        return None
    
def extract_product_id(url: str) -> str | None:
    import re
    match = re.search(r'/item/(\d+)\.html', url)
    return match.group(1) if match else None

def generate_sign(params: dict, secret: str) -> str:
    sorted_items = sorted(params.items())
    sign_str = secret + ''.join(f"{k}{v}" for k, v in sorted_items) + secret
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()