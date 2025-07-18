import json
import httpx
import aiohttp
import asyncio

from urllib.parse import urlparse
from playwright.async_api import async_playwright

ENDPOINT_JSON = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=es&proxy_format=protocolipport&format=json"


async def fetch_raw_proxyscrape_json():
    url = "https://api.proxyscrape.com/v4/free-proxy-list/get"
    params = {
        "request": "display_proxies",
        "country": "es",
        "proxy_format": "protocolipport",
        "format": "json"
    }
    headers = {
        "accept": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            proxies = data.get('proxies')

            filtered = []
            for item in proxies:
                ip = item.get("ip")
                port = item.get("port")
                protocol = item.get("protocol")
                proxy = item.get("proxy")

                works = await test_proxy_pw(proxy)

                if proxy and works: # ip and port and protocol:
                    filtered.append({
                            "proxy": proxy
                            #"ip": ip, 
                            #"port": port,
                            #"protocol": protocol
                        }
                    )

            print(filtered)

            return data

    except Exception as e:
        print(f"[ERROR] Fallo al obtener proxies: {e}")
        return []
    

async def fetch_proxies_from_proxyscrape_as_json() -> list[dict]:
    """
    Descarga una lista de proxies gratuitos desde ProxyScrape para España.
    Devuelve una lista de objetos JSON como: { "server": "http://ip:port" }

    Returns:
        list[dict]: Lista de proxies en formato JSON.
    """
    url = (
        "https://api.proxyscrape.com/v4/free-proxy-list/get"
        "?request=display_proxies&country=es&proxy_format=protocolipport&format=json"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            raw_proxies = response.text.splitlines()

            proxies = [{"server": f"http://{line.strip()}"} for line in raw_proxies if line.strip()]
            return proxies

    except Exception as e:
        print(f"[ERROR] No se pudieron obtener los proxies: {e}")
        return []

async def fetch_proxies_for_playwright() -> list[dict]:
    """
    Descarga proxies HTTP de ProxyScrape (España) y los transforma en dicts compatibles
    con Playwright: {server, username, password}. Filtra IPv6 automáticamente.
    """
    url = (
        "https://api.proxyscrape.com/v4/free-proxy-list/get"
        "?request=display_proxies&country=es&proxy_format=protocolipport&format=json"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            raw = resp.text.splitlines()

            proxy_dicts = []
            for line in raw:
                line = line.strip()
                if not line or "[" in line or "]" in line:
                    continue  # descarta líneas vacías o IPv6

                # añade protocolo si falta
                if "://" not in line:
                    line = "http://" + line

                try:
                    parsed = urlparse(line)
                    if not parsed.hostname or not parsed.port:
                        continue
                    proxy_dicts.append({
                        "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
                        "username": parsed.username,
                        "password": parsed.password
                    })
                except Exception as e:
                    print(f"[WARN] Proxy descartado '{line}': {e}")

            return proxy_dicts

    except Exception as e:
        print(f"[ERROR] No se pudieron obtener los proxies: {e}")
        return []

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

async def test_proxy_pw(server: str, username: str = None, password: str = None):
    try:
        async with async_playwright() as p:
            proxy = {"server": server}
            if username and password:
                proxy["username"] = username
                proxy["password"] = password

            print(f"🌐 Probando proxy: {proxy}")

            browser = await p.chromium.launch(proxy=proxy)
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()
            await page.goto("https://api.myip.com", timeout=15000)  # 15 segundos máx
            content = await page.content()
            print(content)
            await browser.close()
            return True

    except Exception as e:
        print(f"❌ Error al probar proxy: {e}")
        return False


# 🧪 Ejemplo de uso
async def main():
    proxies = await fetch_proxies_for_playwright()
    print(f"✅ Se cargaron {len(proxies)} proxies:")
    for p in proxies[:5]:
        print(p)

if __name__ == "__main__":
    #asyncio.run(main())
    asyncio.run(fetch_raw_proxyscrape_json())