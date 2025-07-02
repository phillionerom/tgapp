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

aliexpress = AliExpressSDK(ALIEXPRESS_APP_KEY, ALIEXPRESS_APP_SECRET, ALIEXPRESS_TRACKING_ID)


async def get_product(message_id, channel, product_url):
    print(f"ALI product url={product_url}")
    final_url = await resolve_aliexpress_redirect(product_url)
    print(f"ALI resolved url={final_url}")

    clean_url = aliexpress.clean_url(final_url)

    aff_link = aliexpress.generate_affiliate_link(clean_url)

    print("AliExpress AFF LINK =", aff_link)
    print("AliExpress CLEAN URL =", clean_url)

    product = await get_aliexpress_product_info(message_id, channel, clean_url)

    return product

async def get_aliexpress_product_info(message_id, channel: str, url: str) -> dict | None:
    product_id = extract_product_id(url)
    if not product_id:
        print("[AliExpress] ❌ Could not extract product ID from URL.")
        return None

    # API call
    method = "api.product.get"
    timestamp = str(int(time.time() * 1000))
    api_path = "openapi/param2/2/portals.open/api.product.get"
    base_url = f"https://api.aliexpress.com/{api_path}/{ALIEXPRESS_APP_KEY}"

    params = {
        "app_key": ALIEXPRESS_APP_KEY,
        "timestamp": timestamp,
        "sign_method": "hmac-sha256",
        "product_id": product_id,
        "tracking_id": ALIEXPRESS_TRACKING_ID,
    }

    # Generate sign
    query = urlencode(sorted(params.items()))
    sign_str = f"{api_path}/{ALIEXPRESS_APP_KEY}{query}"
    sign = hmac.new(ALIEXPRESS_APP_SECRET.encode(), sign_str.encode(), hashlib.sha256).hexdigest().upper()
    params["sign"] = sign

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(base_url, params=params)
            if res.headers.get("Content-Type", "").startswith("application/json"):
                data = res.json()
                result = data.get("result", {})
                if result.get("image_url"):
                    product_image = await download_image_from_url(image, f"images/aliexpress/{channel}-{message_id}_product.jpg")
                    return {
                        "product_image": product_image,
                        "title": result.get("product_title", ""),
                        "current_price": result.get("sale_price", ""),
                        "category": result.get("target_country", ""),
                        "original_price": 0,
                        "savings_percent": 0,
                        "my_product_url": url,
                        "product_code": product_id
                    }
            else:
                print("[AliExpress API] ❌ Response is not JSON. Falling back to HTML scraping.")
    except Exception as e:
        print(f"[AliExpress API] ❌ Error during request: {e}")

    # Fallback: scrape HTML
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