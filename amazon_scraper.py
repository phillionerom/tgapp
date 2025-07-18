import re
import random
import requests
import asyncio

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from utils.net_utils import get_random_desktop_user_agent

# Free proxies from free-proxy-list.net
# Updated at 2025-06-25 14:52:03 UTC.

# Lista de proxies (formato: http://user:pass@ip:port o http://ip:port)
PROXIES = [
    "http://250718GJsc2-resi_region-ES_Andalusia_Cordoba:GrRSU1iB3dp6sRo@eu.proxy-jet.io:1010",
    "http://250718GJsc2-resi_region-ES_Andalusia_Cordoba:GrRSU1iB3dp6sRo@eu.proxy-jet.io:1010",
    "http://250718GJsc2-resi_region-ES_Andalusia_Cordoba:GrRSU1iB3dp6sRo@eu.proxy-jet.io:1010",
    "http://250718GJsc2-resi_region-ES_Andalusia_Cordoba:GrRSU1iB3dp6sRo@eu.proxy-jet.io:1010"
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

        try:
            async with async_playwright() as p:
                browser_args = {
                    "headless": True,  # False: to debug
                    "args": ["--blink-settings=imagesEnabled=false"] # https://peter.sh/experiments/chromium-command-line-switches/ disable images
                }

                proxy = None
                if use_proxy:
                    proxy_url = random.choice(PROXIES)
                    proxy = parse_proxy_url(proxy_url)
                    browser_args["proxy"] = proxy

                print(f"Browser args will be: {browser_args}")

                browser = await p.chromium.launch(**browser_args)
                context = await browser.new_context(
                    user_agent=get_random_desktop_user_agent(),
                    locale="es-ES",
                    viewport={"width": 1280, "height": 800},
                    ignore_https_errors=True
                )

                await context.set_extra_http_headers({
                    "Accept": "text/html"
                })

                page = await context.new_page()

                # Avoid to playwright to download images, since it is not needed, just the img.src
                await page.route("**/*", block_unneeded)
                # await page.route("**/*", lambda route, request: (
                #     route.abort() if request.resource_type == "image" else route.continue_()
                # ))

                await asyncio.sleep(random.uniform(2, 5))  # pausa inicial aleatoria

                print(f"\n🕵️ Attempt {attempt+1} - Using proxy: {proxy or '(NO PROXY)'}\n")
                await page.goto(product_url, timeout=60000)
                #await page.wait_for_load_state("networkidle")
                #await page.wait_for_selector("#imgTagWrapperId img", timeout=30000)
                await page.wait_for_selector("#imgTagWrapperId img", state="attached", timeout=30000)
                await asyncio.sleep(random.uniform(1, 3))  # comportamiento humano

                # Imagen principal
                print(f"Reading product image...")
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
                category_selectors = [
                    "#wayfinding-breadcrumbs_feature_div li a",
                    "#desktop-breadcrumbs_feature_div li a"
                ]
                category = None

                for sel in category_selectors:
                    try:
                        locator = page.locator(sel).first
                        category = await locator.text_content(timeout=2000)
                        if category:
                            category = category.strip()
                            break
                    except Exception:
                        continue

                # Debug purposes
                #html = await page.content()
                #with open(f"debug_attempt_{attempt+1}.html", "w", encoding="utf-8") as f:
                #    f.write(html)

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

def parse_proxy_url(proxy_url: str) -> dict:
    parsed = urlparse(proxy_url)
    return {
        "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
        "username": parsed.username,
        "password": parsed.password
    }

blocked_types = {"image", "stylesheet", "font", "media", "other"}

async def block_unneeded(route, request):
    if request.resource_type in blocked_types:
        #print(f"🛑 Bloqueada ({request.resource_type}): {request.url}")
        await route.abort()
    elif any(domain in request.url for domain in [
        "media-amazon.com", "ssl-images-amazon.com"
    ]):
        #print(f"⛔ BLOCKED domain: {request.url}")
        await route.abort()
    else:
        await route.continue_()

async def block_images(route, request):
    if request.resource_type == "image":
        #print(f"🛑 Bloqueando imagen: {request.url}")
        await route.abort()
    else:
        await route.continue_()