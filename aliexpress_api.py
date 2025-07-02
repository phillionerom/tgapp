import time
import hashlib
import hmac
import base64
import requests

from urllib.parse import urlencode
from urllib.parse import urlparse, urlunparse

from config import ALIEXPRESS_APP_KEY, ALIEXPRESS_APP_SECRET, ALIEXPRESS_TRACKING_ID


def generate_signed_params(api_name: str, params: dict) -> dict:
    timestamp = str(int(time.time() * 1000))

    base_params = {
        "app_key": ALIEXPRESS_APP_KEY,
        "timestamp": timestamp,
        "sign_method": "hmac-sha256"
    }

    all_params = {**base_params, **params}
    sorted_params = dict(sorted(all_params.items()))

    query = urlencode(sorted_params)
    string_to_sign = f"param2/2/portals.open/{api_name}/{ALIEXPRESS_APP_KEY}{query}"

    sign = hmac.new(ALIEXPRESS_APP_SECRET.encode(), string_to_sign.encode(), hashlib.sha256).hexdigest().upper()

    return {**sorted_params, "sign": sign}

def generate_affiliate_link(product_url: str) -> str | None:
    api_name = "api.link.generate"
    params = {
        "promotion_link": product_url,
        "tracking_id": ALIEXPRESS_TRACKING_ID
    }

    signed_params = generate_signed_params(api_name, params)

    url = f"https://api.aliexpress.com/openapi/param2/2/portals.open/{api_name}/{ALIEXPRESS_APP_KEY}"
    
    try:
        response = requests.get(url, params=signed_params)

        try:
            data = response.json()
        except Exception:
            print(f"[AliExpress API] ❌ Response is not JSON: {response.text}")
            return None

        if data.get("result") and data["result"].get("promotion_link"):
            return data["result"]["promotion_link"]

        print(f"[AliExpress API] Response: {data}")
        return None
    except Exception as e:
        print(f"[AliExpress API] Error: {e}")
        return None


def clean_url(url: str) -> str:
    parsed = urlparse(url)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
    return clean_url