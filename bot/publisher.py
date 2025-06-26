from aiogram import Bot
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from config import DON_OFERTON_BOT_TOKEN
import os

bot = Bot(token=DON_OFERTON_BOT_TOKEN, parse_mode="HTML")


async def send_promotional_message(chat_id: str, text: str, image_path: str = None, button_url: str = None):
    try:
        reply_markup = None
        if button_url:
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton("🔗 Ver Oferta", url=button_url)]
            ])

        if image_path and os.path.exists(image_path):
            photo = InputFile(image_path)
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=text,
                reply_markup=reply_markup
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup
            )

        print(f"✅ Mensaje publicado con éxito")
        return True

    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return False