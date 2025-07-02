from telegram import Bot, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from config import DON_OFERTON_BOT_TOKEN
from publisher.message_builder import build_promotional_message

bot = Bot(token=DON_OFERTON_BOT_TOKEN)

likes_store = {}

# Likes button in the FUTURE...

def build_keyboard(message_id: int, likes: int, product_url: str) -> InlineKeyboardMarkup:
    # return InlineKeyboardMarkup([
    #     [
    #         InlineKeyboardButton(f"❤️ Me gusta ({likes})", callback_data=f"like:{message_id}"),
    #         InlineKeyboardButton("🔗 Ver Oferta", url=product_url)
    #     ]
    # ])
    button_url = product_url
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Ir a la Oferta 🔥", url=button_url)]
    ]) if button_url else None

    return buttons

async def send_post(channel: str, message: dict) -> bool:
    try:
        publication = build_promotional_message(message)

        # # Botón de enlace
        # button_url = message.get("product_url")
        # buttons = InlineKeyboardMarkup([
        #     [InlineKeyboardButton("🔗 Ver Oferta", url=button_url)]
        # ]) if button_url else None

        # buttons = InlineKeyboardMarkup([
        #     [
        #         InlineKeyboardButton("❤️ Me gusta (0)", callback_data=f"like:{message['message_id']}"),
        #         InlineKeyboardButton("🔗 Ver Oferta", url=message["product_url"])
        #     ]
        # ])

        message_id = message["message_id"]
        likes_store[message_id] = 0  # inicializa contador

        keyboard = build_keyboard(message_id, likes_store[message_id], message["product_url"])
        
        if message.get("image"):
            await bot.send_photo(
                chat_id=channel,
                photo=message['image'],
                caption=publication,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
        else:
            await bot.send_message(
                chat_id=channel,
                text=publication,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )

        return True

    except TelegramError as e:
        print(f"[ERROR] TelegramError while sending to {channel}: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error while sending to {channel}: {e}")
        return False

# TODO soon...
async def handle_like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("like:"):
        return

    message_id = int(data.split(":")[1])
    likes_store[message_id] = likes_store.get(message_id, 0) + 1

    new_keyboard = build_keyboard(
        message_id,
        likes_store[message_id],
        product_url="https://ejemplo.com"  # opcional: puedes obtenerla si la guardaste con likes
    )

    try:
        await query.edit_message_reply_markup(reply_markup=new_keyboard)
    except Exception as e:
        print(f"[ERROR] No se pudo actualizar botones: {e}")


# Al iniciar el bot...
# from telegram.ext import ApplicationBuilder

# async def main():
#     app = ApplicationBuilder().token(DON_OFERTON_BOT_TOKEN).build()

#     # Añade manejador para botones
#     app.add_handler(CallbackQueryHandler(handle_like))

#     print("🤖 Bot iniciado. Esperando interacciones...")
#     await app.run_polling()