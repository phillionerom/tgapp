import requests
from config import META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN, IG_USER_ID


def publish(caption: str, image_url: str):
    # Paso 1: Crear el contenedor de medios
    media_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media"
    media_payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }

    media_response = requests.post(media_url, data=media_payload).json()

    if "id" not in media_response:
        print(f"❌ Error creando media: {media_response}")
        return

    creation_id = media_response["id"]

    # Paso 2: Publicar
    publish_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": META_ACCESS_TOKEN
    }

    publish_response = requests.post(publish_url, data=publish_payload).json()

    if "id" in publish_response:
        print(f"✅ Publicado en Instagram con ID: {publish_response['id']}")
    else:
        print(f"❌ Error al publicar: {publish_response}")


def refresh_token():
    url = "https://graph.facebook.com/v23.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": META_APP_ID,
        "client_secret": META_APP_SECRET,
        "fb_exchange_token": META_ACCESS_TOKEN
    }

    res = requests.get(url, params=params).json()

    if "access_token" in res:
        new_token = res["access_token"]
        print(f"✅ Token refreshed: {new_token}")
        # Aquí podrías guardar el nuevo token en tu .env si lo automatizas
        return new_token
    else:
        print(f"❌ Error refreshing token: {res}")
        return None
    
import requests

def get_instagram_user_id(access_token):
    # Paso 1: Obtener las páginas del usuario
    pages_url = "https://graph.facebook.com/v23.0/me/accounts"
    pages_params = {
        "access_token": access_token
    }
    pages_res = requests.get(pages_url, params=pages_params).json()

    if "data" not in pages_res or not pages_res["data"]:
        return "❌ No se encontraron páginas o falta permiso 'pages_show_list'"

    page = pages_res["data"][0]
    page_id = page["id"]
    print(f"✅ Página detectada: {page['name']} (ID: {page_id})")

    # Paso 2: Obtener cuenta de Instagram conectada
    ig_url = f"https://graph.facebook.com/v23.0/{page_id}"
    ig_params = {
        "fields": "instagram_business_account",
        "access_token": access_token
    }
    ig_res = requests.get(ig_url, params=ig_params).json()

    if "instagram_business_account" in ig_res:
        ig_id = ig_res["instagram_business_account"]["id"]
        return f"✅ IG_USER_ID encontrado: {ig_id}"
    else:
        return f"❌ No se pudo obtener instagram_business_account: {ig_res}"
