import re
import random
import requests
import asyncio

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Free proxies from free-proxy-list.net
# Updated at 2025-06-25 14:52:03 UTC.

# Lista de proxies (formato: http://user:pass@ip:port o http://ip:port)
PROXIES = [
    "http://159.89.245.69:53971",
    "http://13.38.66.165:3128",
    "http://13.208.241.126:53233",
    "http://51.81.245.3:17981",
    "http://13.126.217.46:3128",
    "http://38.250.126.201:999",
    "http://23.237.210.82:80",
    "http://195.158.8.123:3128",
    "http://47.239.48.114:59394",
    "http://157.245.124.217:53971",
    "http://43.199.163.10:3128",
    "http://27.79.235.153:16000",
    "http://89.117.145.245:3128",
    "http://38.147.98.190:8080",
    "http://40.76.69.94:8080",
    "http://64.83.246.99:5999",
    "http://200.174.198.86:8888",
    "http://188.166.230.109:31028"
]

# Número máximo de reintentos por URL
MAX_RETRIES = 3


def get_amazon_main_image_by_bs4(product_url: str) -> str | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(product_url, headers=headers, timeout=60)
        soup = BeautifulSoup(response.text, "html.parser")

        img_tag = soup.select_one("#imgTagWrapperId img")
        if img_tag and img_tag.has_attr("src"):
            return img_tag["src"]
    except requests.RequestException as e:
        print(f"exception getting amz img: {e}")
        return None
    

async def get_amazon_main_image(product_url: str) -> str | None:
    """
    Uses Playwright (async) to extract the main image URL from an Amazon product page.
    Requires: pip install playwright && playwright install
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(product_url, timeout=60000)
            img = page.locator("#imgTagWrapperId img")
            src = await img.get_attribute("src")
            await browser.close()
            return src
    except Exception as e:
        print(f"❌ Error using Playwright (async) to get Amazon image: {e}")
        return None
    

def parse_price(price_str):
    if not price_str:
        return None
    price_str = price_str.replace(".", "").replace(",", ".")
    match = re.search(r"\d+(\.\d+)?", price_str)
    return float(match.group(0)) if match else None


async def get_amazon_product_data(product_url: str) -> dict:
    for attempt in range(MAX_RETRIES):
        use_proxy = attempt > 0  # Primer intento sin proxy
        proxy = random.choice(PROXIES) if use_proxy and PROXIES else None

        try:
            async with async_playwright() as p:
                browser_args = {"headless": True}  # False: to debug
                if proxy:
                    browser_args["proxy"] = {"server": proxy}

                browser = await p.chromium.launch(**browser_args)
                page = await browser.new_page()

                await asyncio.sleep(random.uniform(2, 5))  # pausa inicial aleatoria

                print(f"\n🕵️ Attempt {attempt+1} - Using proxy: {proxy or '(NO PROXY)'}\n")
                await page.goto(product_url, timeout=60000)
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(random.uniform(1, 3))  # comportamiento humano

                # Imagen principal
                img = page.locator("#imgTagWrapperId img")
                image_url = await img.get_attribute("src")

                # Precio actual
                price_selectors = [
                    "#priceblock_dealprice",
                    "#priceblock_saleprice",
                    "#priceblock_ourprice",
                    "#corePrice_feature_div span.a-offscreen",
                    "#apex_desktop span.a-offscreen",
                    "span.a-price span.a-offscreen"
                ]
                current_price = None
                for sel in price_selectors:
                    element = page.locator(sel)
                    if await element.count():
                        current_price = await element.nth(0).inner_text()
                        if current_price:
                            break

                # Precio original
                original_price_selectors = [
                    "span.a-text-strike",
                    "#listPrice",
                    "#price span.a-offscreen",
                    "span.a-price span.a-offscreen"
                ]
                original_price = None
                for sel in original_price_selectors:
                    element = page.locator(sel)
                    if await element.count():
                        original_price = await element.nth(0).inner_text()
                        if original_price:
                            break

                # Parsear
                current = parse_price(current_price)
                original = parse_price(original_price)

                if not current or not original:
                    html = await page.content()
                    prices = re.findall(r"\u20ac\s?(\d+[\.,]\d{2})", html)
                    parsed = [parse_price(p) for p in prices if parse_price(p)]
                    if parsed:
                        current = current or parsed[0]
                        if len(parsed) > 1:
                            original = original or parsed[1]

                # Calcular ahorro
                savings = None
                if current and original and original > current:
                    savings = round(100 * (original - current) / original, 2)

                # Categoría
                category = await page.locator("#wayfinding-breadcrumbs_feature_div li a").first.text_content()
                category = category.strip() if category else None

                await browser.close()
                return {
                    "ok": True,
                    "image_url": image_url,
                    "current_price": current,
                    "original_price": original,
                    "savings_percent": savings,
                    "category": category,
                    "proxy_used": proxy
                }

        except Exception as e:
            print(f"❌ Error attempt {attempt+1}: {e}")
            await asyncio.sleep(random.uniform(2, 4))

    return {
        "ok": False,
        "image_url": None,
        "current_price": None,
        "original_price": None,
        "savings_percent": None,
        "category": None,
        "proxy_used": None
    }