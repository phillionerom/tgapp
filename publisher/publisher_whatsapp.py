import httpx

from publisher.message_builder import build_whatsapp_message

SESSION = "default"
CHAT_ID = "120363419707406919@newsletter"


async def publish(chat_id: str, message: dict) -> bool:
    publication = build_whatsapp_message(message)

    url = "http://localhost:3000/api/sendText"
    headers = {
        "Content-Type": "application/json",
        # "X-Api-Key": "yoursecretkey"
    }
    data = {
        "session": SESSION,
        "chatId": chat_id,
        "text": publication
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            res_json = response.json()

        if "id" not in res_json:
            print(f"❌ Failed to send message to chat id {chat_id}. Received response: {res_json}")
            return False

        print(f"💬 Published successfully in chat: {res_json['to']} with ID={res_json['id']['id']}")
        return True

    except Exception as e:
        print(f"❌ Exception while sending message to WhatsApp: {e}")
        return False
