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
from utils.ngrok_utils import start_ngrok_if_needed, get_active_ngrok_tunnel

# CONFIG — reemplaza con tus valores reales
PUBLIC_DIR = "output/pub/ig"
PORT = 8081


def start_local_server():
    os.chdir(PUBLIC_DIR)
    server = HTTPServer(("", PORT), SimpleHTTPRequestHandler)
    print(f"🌍 Serving local files at http://localhost:{PORT}/")
    server.serve_forever()

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
    start_ngrok_if_needed()
    public_url = get_active_ngrok_tunnel()

    if not public_url:
        print("❌ Failed to retrieve ngrok URL.")
        return

    image_url = f"{public_url}/{filename}"
    print(f"🌐 Public image URL: {image_url}")
    publish_to_instagram(image_url, args.caption)


if __name__ == "__main__":
    main()
