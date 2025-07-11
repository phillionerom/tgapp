import os
import shutil
import requests

from config import META_ACCESS_TOKEN, IG_USER_ID
from publisher.message_builder import build_instagram_message
from utils.ngrok_utils import (
    start_local_server,
    get_active_ngrok_tunnel
)

PUBLIC_DIR = "output"
IG_DIR = "pub/ig"


def init_local_server():
    start_local_server(PUBLIC_DIR)

    public_url = get_active_ngrok_tunnel()

    if not public_url:
        print("❌ Failed to retrieve ngrok URL.")
        return None
    
    return public_url

def image_exists(relative_path: str) -> bool:
    # Ruta absoluta basada en la ubicación del script que se está ejecutando
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(base_dir, relative_path)
    return os.path.exists(abs_path)

def prepare_image_local(image_path: str) -> str:
    image_filename = os.path.basename(image_path)
    image_path = os.path.join("output", image_filename)
    abs_image_path = os.path.abspath(image_path)

    if not os.path.exists(abs_image_path):
        raise FileNotFoundError(f"[ERROR] Image does not exist: {abs_image_path}")

    dest_dir = os.path.abspath(os.path.join(PUBLIC_DIR, IG_DIR))
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = os.path.join(dest_dir, image_filename)

    if abs_image_path != dest_path:
        shutil.copy(abs_image_path, dest_path)
        print(f"✅ Image copied to public dir.")
    else:
        print(f"ℹ️ Image already in destination, skipping copy.")

    return os.path.join(IG_DIR, image_filename)  # Esto se usará para generar la URL

def publish(message):
    public_url = init_local_server()

    if public_url is None:
        return False
    
    filename = prepare_image_local(message['image'])
    image_url = f"{public_url}/{filename}"

    publication = build_instagram_message(message)

    print(f"🌐 Public image URL: {image_url}")

    print(f"📸 Step 1: Creating IG media container...")
    res = requests.post(
        f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media",
        data={
            "image_url": image_url,
            "caption": publication,
            "access_token": META_ACCESS_TOKEN
        }
    ).json()

    if "id" not in res:
        print(f"❌ Failed to create IG media: {res}")
        return False

    creation_id = res["id"]

    print(f"✅ IG Media container created: {creation_id}")

    print("📤 Step 2: Publishing media...")
    publish_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": META_ACCESS_TOKEN
    }
    publish_res = requests.post(publish_url, data=publish_payload).json()

    if "id" in publish_res:
        print(f"✅ Published successfully: Post ID {publish_res['id']}\n")
        return True
    else:
        print(f"❌ Failed to publish: {publish_res}\n")
        return False
