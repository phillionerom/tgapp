import os
import time
import socket
import requests
import subprocess

from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

PORT = 8081
NGROK_API = "http://localhost:4040/api/tunnels"


def start_local_server(public_dir):
    os.makedirs(public_dir, exist_ok=True)

    class LocalHTTPHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=public_dir, **kwargs)

    if is_port_in_use(PORT):
        print(f"ℹ️ Local server already running at http://localhost:{PORT}/")
    else:
        handler = lambda *args, **kwargs: LocalHTTPHandler(*args, **kwargs)
        server = HTTPServer(("", PORT), handler)
        Thread(target=server.serve_forever, daemon=True).start()
        print(f"🌍 Serving at http://localhost:{PORT}/")

    start_ngrok_if_needed()

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

def get_active_ngrok_tunnel(port=8081):
    try:
        tunnels = requests.get(NGROK_API).json().get("tunnels", [])
        for tunnel in tunnels:
            config = tunnel.get("config", {})
            if f":{port}" in config.get("addr", ""):
                return tunnel["public_url"]
    except Exception as e:
        print(f"[ngrok_utils] Error checking tunnels: {e}")
    return None

def start_ngrok_if_needed(port=8081):
    try:
        if get_active_ngrok_tunnel(port):
            print("ℹ️ Ngrok already running on port", port)
            return

        print("🚀 Starting ngrok tunnel...")
        subprocess.Popen(["ngrok", "http", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
    except Exception as e:
        print(f"[ngrok_utils] Error starting ngrok: {e}")
