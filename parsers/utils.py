import os
import re
import requests
import aiohttp

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from config import DEFAULT_AMAZON_TAG


def extract_first_url(text: str) -> str | None:
    url_pattern = r'(https?://[^\s]+)'
    match = re.search(url_pattern, text)
    return match.group(0) if match else None


def resolve_redirect_url(short_url: str, timeout: float = 5.0) -> str | None:
    try:
        response = requests.head(short_url, allow_redirects=True, timeout=timeout)
        return response.url
    except requests.RequestException:
        return None


def replace_amazon_affiliate_tag(url: str, new_tag: str = DEFAULT_AMAZON_TAG) -> str:
    parsed = urlparse(url)

    if 'amazon.' not in parsed.netloc:
        return url  # Not an Amazon URL

    query = parse_qs(parsed.query)
    query['tag'] = [new_tag]  # Replace or insert tag param

    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def extract_asin_from_url(url: str) -> str | None:
    """
    Extract the ASIN from an Amazon URL.
    Examples:
    https://www.amazon.es/dp/B0CRCG7816 -> B0CRCG7816
    https://www.amazon.es/gp/product/B0CRCG7816?tag=... -> B0CRCG7816
    """
    match = re.search(r"/(dp|gp/product)/([A-Z0-9]{10})", url)
    return match.group(2) if match else None


def detect_store_from_url(url: str) -> str | None:
    """
    Detect the e-commerce store from a URL.
    Returns one of: 'amazon', 'aliexpress', 'miravia', 'unknown'
    """
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()

    if 'amazon.' in netloc:
        return 'amazon'
    elif 'aliexpress.' in netloc:
        return 'aliexpress'
    elif 'miravia.' in netloc:
        return 'miravia'
    elif 'carrefour.' in netloc:
        return 'carrefour'
    elif 'ebay.' in netloc:
        return 'ebay'
    else:
        print(f"- Unknown vendor found for url: {url}")
        return 'unknown'
    

async def download_image_from_url(url: str, dest_path: str) -> str | None:
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(dest_path, 'wb') as f:
                        f.write(await resp.read())
                    return dest_path
                else:
                    print(f"⚠️ Error downloading image: HTTP {resp.status}")
    except Exception as e:
        print(f"❌ Exception downloading image: {e}")
    return None