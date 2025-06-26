from telegram import Bot, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

from config import DON_OFERTON_BOT_TOKEN

bot = Bot(token=DON_OFERTON_BOT_TOKEN)


async def send_message_with_bot(chat_id: str, text: str, image_path: str = None, button_url: str = None):
    try:
        buttons = None
        if button_url:
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Ver Oferta", url=button_url)]
            ])

        if image_path:
            with open(image_path, "rb") as photo:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=text,
                    reply_markup=buttons
                )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=buttons
            )

        print(f"✅ Mensaje publicado con bot")
        return True

    except TelegramError as e:
        print(f"❌ Error enviando mensaje con bot: {e}")
        return False