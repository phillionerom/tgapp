import os
import shutil
import subprocess
import time
import requests
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode
import argparse

from config import META_ACCESS_TOKEN, IG_USER_ID

# CONFIG — reemplaza con tus valores reales
PUBLIC_DIR = "output/pub/ig"
PORT = 8081
NGROK_API = "http://localhost:4040/api/tunnels"


def start_local_server():
    os.chdir(PUBLIC_DIR)
    server = HTTPServer(("", PORT), SimpleHTTPRequestHandler)
    print(f"🌍 Serving local files at http://localhost:{PORT}/")
    server.serve_forever()


def start_ngrok():
    print("🚀 Starting ngrok tunnel...")
    subprocess.Popen(["ngrok", "http", str(PORT)], stdout=subprocess.DEVNULL)
    time.sleep(2)


def get_ngrok_url():
    for _ in range(10):
        try:
            tunnels = requests.get(NGROK_API).json()
            for tunnel in tunnels["tunnels"]:
                if tunnel["proto"] == "https":
                    return tunnel["public_url"]
        except:
            time.sleep(1)
    return None


def prepare_image(image_path: str) -> str:
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    filename = os.path.basename(image_path)
    dest = os.path.join(PUBLIC_DIR, filename)
    shutil.copy(image_path, dest)
    return filename


def publish_to_instagram(image_url: str, caption: str):
    print(f"📸 Step 1: Creating media container...")
    url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }
    res = requests.post(url, data=payload).json()

    if "id" not in res:
        print(f"❌ Failed to create media: {res}")
        return

    creation_id = res["id"]
    print(f"✅ Media container created: {creation_id}")

    print("📤 Step 2: Publishing media...")
    publish_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": META_ACCESS_TOKEN
    }
    publish_res = requests.post(publish_url, data=publish_payload).json()
    if "id" in publish_res:
        print(f"✅ Published successfully: Post ID {publish_res['id']}")
    else:
        print(f"❌ Failed to publish: {publish_res}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to local image")
    parser.add_argument("caption", help="Caption for Instagram post")
    args = parser.parse_args()

    filename = prepare_image(args.image)
    Thread(target=start_local_server, daemon=True).start()
    start_ngrok()
    public_url = get_ngrok_url()

    if not public_url:
        print("❌ Failed to retrieve ngrok URL.")
        return

    image_url = f"{public_url}/{filename}"
    print(f"🌐 Public image URL: {image_url}")
    publish_to_instagram(image_url, args.caption)


if __name__ == "__main__":
    main()
