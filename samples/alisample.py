import hashlib
import time
import requests

from config import ALIEXPRESS_APP_KEY, ALIEXPRESS_APP_SECRET

PRODUCT_ID = "1005008063959259"

def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def generate_sign(params: dict, secret: str) -> str:
    sorted_items = sorted(params.items())
    sign_str = secret + ''.join(f"{k}{v}" for k, v in sorted_items) + secret
    md5 = hashlib.md5()
    md5.update(sign_str.encode('utf-8'))
    return md5.hexdigest().upper()

def main():
    params = {
    "method": "aliexpress.affiliate.productdetail.get",
    "app_key": ALIEXPRESS_APP_KEY,
    "timestamp": get_timestamp(),
    "format": "json",
    "v": "2.0",
    "sign_method": "md5",
    "product_ids": PRODUCT_ID,
    "target_currency": "EUR",
    "target_language": "ES"
}

    params["sign"] = generate_sign(params, ALIEXPRESS_APP_SECRET)

    response = requests.post("https://api-sg.aliexpress.com/sync", data=params)
    print(response.json())

def test():
    response = requests.post("https://api-sg.aliexpress.com/sync", data={
    "method": "aliexpress.affiliate.category.get",
    "app_key": ALIEXPRESS_APP_KEY,
    "timestamp": "2025-07-04 12:00:00",
    "format": "json",
    "v": "2.0",
    "sign_method": "md5",
    "sign": "DUMMY"
    })
    print(response.json())


if __name__ == "__main__":
    main()
    #test()
