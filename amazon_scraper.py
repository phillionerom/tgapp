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
    "http://brd-customer-hl_0dfcb399-zone-residential_proxy1-country-es:viyvj0uqlu65@brd.superproxy.io:33335"
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
    price_str = str(price_str).replace(".", "").replace(",", ".")
    match = re.search(r"\d+(\.\d+)?", price_str)
    return float(match.group(0)) if match else None


async def get_amazon_product_data(product_url: str) -> dict:
    for attempt in range(MAX_RETRIES):
        use_proxy = attempt > 0  # Primer intento sin proxy
        proxy = random.choice(PROXIES) if use_proxy and PROXIES else None

        try:
            async with async_playwright() as p:
                browser_args = {"headless": True}  # False: to debug

                newproxy = {
                    "server": "http://brd.superproxy.io:33335",
                    "username": "brd-customer-hl_0dfcb399-zone-residential_proxy1-country-es",
                    "password": "viyvj0uqlu65"
                }

                if proxy:
                    browser_args["proxy"] = {"server": newproxy}

                browser = await p.chromium.launch(**browser_args)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                    locale="es-ES",
                    viewport={"width": 1280, "height": 800}
                )
                page = await context.new_page()

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

                await context.close()
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
            try:
                html = await page.content()
                with open(f"error_attempt_{attempt+1}.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"📝 HTML guardado como error_attempt_{attempt+1}.html")
            except Exception as inner:
                print(f"⚠️ No se pudo capturar el HTML: {inner}")
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