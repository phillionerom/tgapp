import asyncio
import aiohttp
from typing import List

# Lista de proxies a probar
PROXIES = [
    "http://43.154.134.238:50001",
    "http://135.234.106.253:80",
    "http://57.129.81.201:8080",
    "http://40.76.69.94:8080",
    "http://38.147.98.190:8080",
    "http://195.158.8.123:3128",
    "http://102.222.161.143:3128",
    "http://47.239.8.6:59394",
    "http://35.177.23.165:10535",
    "http://161.35.98.111:8080",
    "http://8.222.17.214:1080",
    "http://159.69.57.20:8880",
    "http://54.210.19.156:3128",
    "http://103.237.144.232:1311",
    "http://47.236.37.129:18081",
    "http://52.78.241.34:3128",
    "http://172.233.78.254:7890",
    "http://56.155.38.121:12736",
    "http://51.84.110.224:3128",
    "http://72.10.160.94:5623",
    "http://72.10.160.173:19329",
    "http://47.239.48.114:59394",
    "http://13.245.30.86:3128",
    "http://43.216.148.22:37425",
    "http://67.43.228.252:33053",
    "http://64.83.246.99:5999",
    "http://67.43.228.254:1905",
    "http://179.60.53.28:999",
    "http://116.103.27.123:16000",
    "http://31.40.248.2:8080",
    "http://3.26.174.5:18609",
    "http://35.179.146.181:3128",
    "http://51.81.245.3:17981",
    "http://8.209.255.13:3128",
    "http://38.250.126.201:999",
    "http://13.235.246.116:25396",
    "http://54.180.239.137:28136",
    "http://52.210.15.148:3128",
    "http://67.43.228.251:14491",
    "http://72.10.160.172:16377",
    "http://186.179.169.22:3128",
    "http://13.208.241.126:53233",
    "http://72.10.160.90:3581",
    "http://13.57.11.118:3128",
    "http://188.245.239.104:4001",
    "http://16.171.242.247:57",
    "http://67.43.236.18:3927",
    "http://113.160.132.195:8080",
    "http://72.10.160.91:18749",
    "http://85.206.93.105:8080",
    "http://67.43.228.250:7015",
    "http://67.43.236.19:19801",
    "http://8.210.117.141:8888",
    "http://3.141.38.145:3128",
    "http://3.126.92.60:29",
    "http://89.117.145.245:3128",
    "http://70.36.101.234:60003",
    "http://200.174.198.86:8888",
    "http://43.199.163.10:3128",
    "http://188.166.230.109:31028",
    "http://72.10.160.170:3949",
    "http://43.217.134.23:3128",
    "http://20.27.11.248:8561",
    "http://20.27.15.111:8561",
    "http://18.60.111.249:6698",
    "http://147.75.34.105:443",
    "http://47.89.159.212:1080",
    "http://94.141.123.62:1080",
    "http://18.101.7.10:3128",
    "http://67.43.236.21:31517",
    "http://37.27.140.130:8005",
    "http://51.44.163.128:3128",
    "http://67.43.236.22:5747",
    "http://3.27.237.252:3128",
    "http://103.81.194.120:8080",
    "http://43.217.116.234:16170",
    "http://154.236.177.103:1977",
    "http://42.96.16.176:1312",
    "http://13.126.217.46:3128",
    "http://18.132.14.119:3128",
    "http://47.236.163.74:8080",
    "http://94.131.12.165:10808",
    "http://72.10.160.92:1801",
    "http://147.75.88.115:9443",
    "http://103.161.34.214:7777",
    "http://116.103.25.149:16000",
    "http://157.245.124.217:53971",
    "http://54.219.112.136:3128",
    "http://159.89.245.69:53971",
    "http://23.237.210.82:80",
    "http://47.91.104.88:3128",
    "http://47.243.92.199:3128",
    "http://43.216.143.123:9008",
    "http://13.38.66.165:3128",
    "http://27.79.233.185:16000",
    "http://147.45.178.211:14658",
    "http://72.10.160.171:18351",
    "http://27.79.235.153:16000",
    "http://43.129.66.216:59394",
    "http://18.171.55.201:3128"
]

PROXIES2 = [
    "http://brd-customer-hl_0dfcb399-zone-residential_proxy1-country-es:viyvj0uqlu65@brd.superproxy.io:33335"
]

TEST_URL = "https://httpbin.org/ip"  # Servicio simple para testear IP
TIMEOUT = 10


async def test_proxy(session: aiohttp.ClientSession, proxy: str) -> str:
    try:
        async with session.get(TEST_URL, proxy=proxy, timeout=TIMEOUT) as response:
            if response.status == 200:
                json_resp = await response.json()
                print(f"✅ Proxy válido: {proxy} → IP: {json_resp.get('origin')}")
                return proxy
            else:
                print(f"⚠️ Proxy inválido (status {response.status}): {proxy}")
    except Exception as e:
        print(f"❌ Proxy falló: {proxy} - {e}")
    return None


async def validate_proxies(proxies: List[str]) -> List[str]:
    valid_proxies = []
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [test_proxy(session, proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks)
        valid_proxies = [proxy for proxy in results if proxy]
    return valid_proxies


if __name__ == "__main__":
    valid = asyncio.run(validate_proxies(PROXIES2))
    print("\n✅ Proxies válidos:")
    for vp in valid:
        print(vp)
