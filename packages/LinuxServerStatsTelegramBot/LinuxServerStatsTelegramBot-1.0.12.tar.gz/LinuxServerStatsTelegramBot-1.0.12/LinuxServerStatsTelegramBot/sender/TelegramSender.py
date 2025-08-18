from LinuxServerStatsTelegramBot.DI import DI
from LinuxServerStatsTelegramBot.sender.Sender import Sender
from telegram import Bot


class TelegramSender(Sender):
    bot: Bot
    chat_id: str

    def __init__(self, chat_id=None):
        self.bot = Bot(token=DI.get_tg_bot_token())
        self.chat_id = chat_id if chat_id else DI.get_tg_chat_id()

    async def send_message(self, message: str) -> None:
        await self.bot.sendMessage(chat_id=self.chat_id, text=message)

    async def send_image(self, image_path: str) -> None:
        await self.bot.sendPhoto(chat_id=self.chat_id, photo=open(image_path, "rb"))

    async def send_sticker(self, sticker_path: str) -> None:
        await self.bot.sendSticker(chat_id=self.chat_id, sticker=open(sticker_path, "rb"))

    async def send_file(self, document_path: str):
        with open(document_path, "rb") as file:
            await self.bot.sendDocument(chat_id=self.chat_id, document=file, filename=document_path)
