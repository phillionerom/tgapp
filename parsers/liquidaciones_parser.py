from telethon.types import Message

from parsers.base_parser import BaseParser


class LiquidacionesParser(BaseParser):
    channel = "liquidaciones"

    async def parse(self, message: Message) -> dict | None:
        return await super().parse(message)