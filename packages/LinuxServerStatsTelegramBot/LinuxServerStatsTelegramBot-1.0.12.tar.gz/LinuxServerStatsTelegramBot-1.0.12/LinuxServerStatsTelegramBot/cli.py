import asyncio

import click

from LinuxServerStatsTelegramBot.DI import DI
from LinuxServerStatsTelegramBot.core.Invoker import Invoker
from LinuxServerStatsTelegramBot.sender.TelegramSender import TelegramSender


# @click.command()
async def notify_server_stats():
    DI.set_sender(TelegramSender())
    await Invoker.send_server_stats_as_images()
    await Invoker.send_server_stats_as_text()


if __name__ == "__main__":
    asyncio.run(notify_server_stats())
