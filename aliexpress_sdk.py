import time
import uuid
import hashlib
import hmac
import requests

from urllib.parse import urlencode, urlparse, urlunparse, quote


class AliExpressSDK:
    API_HOST = "https://api.aliexpress.com"
    API_PATH = "openapi/param2/2/portals.open/api.link.generate"

    def __init__(self, app_key: str, app_secret: str, tracking_id: str, max_retries: int = 3):
        self.app_key = app_key
        self.app_secret = app_secret
        self.tracking_id = tracking_id
        self.max_retries = max_retries

    def clean_url(self, url: str) -> str:
        parsed = urlparse(url)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

    def generate_signed_params(self, promotion_link: str) -> dict:
        timestamp = str(int(time.time() * 1000))
        base_params = {
            "app_key": self.app_key,
            "timestamp": timestamp,
            "sign_method": "hmac-sha256",
            "promotion_link": promotion_link,
            "tracking_id": self.tracking_id
        }
        sorted_params = dict(sorted(base_params.items()))
        query = urlencode(sorted_params)
        string_to_sign = f"{self.API_PATH}/{self.app_key}{query}"
        sign = hmac.new(self.app_secret.encode(), string_to_sign.encode(), hashlib.sha256).hexdigest().upper()
        sorted_params["sign"] = sign
        return sorted_params

    def generate_manual_affiliate_link(self, product_url: str) -> str:
        """
        Builds a manual fallback affiliate link using realistic parameters from AliExpress affiliate portal.
        """
        # Simular un código de seguimiento coherente
        ts = int(time.time() * 1000)
        short_code = f"_{uuid.uuid4().hex[:8]}"
        trace_key = f"{uuid.uuid4().hex}-{ts}-06742-{short_code}"
        terminal_id = "e640b57ead684c7491d2b7ef5eaf7e42"  # Fijo o configurable desde settings

        params = {
            "aff_fcid": trace_key,
            "aff_fsk": short_code,
            "aff_platform": "portals-billboard-hd",
            "sk": short_code,
            "aff_trace_key": trace_key,
            "terminal_id": terminal_id,
            "afSmartRedirect": "y"
        }

        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{product_url}?{query}"

    def generate_affiliate_link(self, product_url: str) -> str:
        """Try to generate an affiliate link via API; fallback to manual if it fails."""
        clean_url = self.clean_url(product_url)
        params = self.generate_signed_params(clean_url)
        url = f"{self.API_HOST}/{self.API_PATH}/{self.app_key}"

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(url, params=params, timeout=10)

                if response.headers.get("Content-Type", "").startswith("text/html"):
                    if "Page under maintenance" in response.text:
                        print(f"[AliExpress API] ⚠️ Maintenance mode (attempt {attempt})")
                        time.sleep(2)
                        continue
                    else:
                        print(f"[AliExpress API] ❌ Unexpected HTML (attempt {attempt})")
                        break

                data = response.json()
                if data.get("result", {}).get("promotion_link"):
                    return data["result"]["promotion_link"]

                print(f"[AliExpress API] ⚠️ No link returned (attempt {attempt}): {data}")
                time.sleep(2)

            except Exception as e:
                print(f"[AliExpress API] ❌ Error (attempt {attempt}): {e}")
                time.sleep(2)

        # Fallback
        print("[AliExpress API] 🔁 Falling back to manual affiliate link")
        return self.generate_manual_affiliate_link(clean_url)
