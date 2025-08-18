#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import asyncio
import logging
from telegram.ext import (Updater, CommandHandler, MessageHandler, filters, Application, ApplicationBuilder)

# Enable logging
from LinuxServerStatsTelegramBot.DI import DI
from LinuxServerStatsTelegramBot.commmand.CpuStats import CpuStats
from LinuxServerStatsTelegramBot.commmand.CronStats import CronStats
from LinuxServerStatsTelegramBot.commmand.DateAndLocation import DateAndLocation
from LinuxServerStatsTelegramBot.commmand.DiskStats import DiskStats
from LinuxServerStatsTelegramBot.commmand.DockerStats import DockerStats
from LinuxServerStatsTelegramBot.commmand.MemoryStats import MemoryStats
from LinuxServerStatsTelegramBot.commmand.CleanMemory import CleanMemory
from LinuxServerStatsTelegramBot.commmand.RebootApp import RebootApp
from LinuxServerStatsTelegramBot.commmand.RebootContainer import RebootContainer
from LinuxServerStatsTelegramBot.commmand.ServersHealth import ServersHealth
from LinuxServerStatsTelegramBot.core.Invoker import Invoker
from LinuxServerStatsTelegramBot.sender.TelegramSender import TelegramSender

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    logger.info(f"Received command start with {update} in the context: {context}")
    update.message.reply_text("Hi!")


async def help(update, context):
    """Send a message when the command /help is issued."""
    help_text = """
    Available commands:
    /cron               : Create a image with Cron stats
    /dateandlocation    : Create a image with Server Date and location
    /disk               : Create a image with Disks stats
    /docker             : Create a image with Docker stats
    /cpu                : Create a image with CPU stats
    /memory             : Create a image with Server Memory stats
    /reports            : Create a zip containing all reports as text files 
    /cleanmemory        : Execute a command to clear the cache and garbage memory 
    /servershealth      : Create a image with the servers health status
    /rebootapp          : Reboot a application managed by docker containers
    /rebootcontainer    : Reboot a docker container
    
    """
    await update.message.reply_text(help_text)


async def rebootapp(update, context):
    if len(context.args) > 0:
        application_name = context.args[0]
        await update.message.reply_text("Rebooting application...")
        chat_id = update.message.from_user.id
        DI.set_sender_temporarily(TelegramSender(str(chat_id)))
        await Invoker.send_data_as_image(RebootApp(application_name))
        await update.message.reply_text("Application rebooted...")
        DI.set_original_sender()
    else:
        await update.message.reply_text(RebootApp().missing_container_name())


async def rebootcontainer(update, context):
    if len(context.args) > 0:
        container_name = context.args[0]
        await update.message.reply_text("Rebooting container...")
        chat_id = update.message.from_user.id
        DI.set_sender_temporarily(TelegramSender(str(chat_id)))
        await Invoker.send_data_as_image(RebootContainer(container_name))
        await update.message.reply_text("Container rebooted...")
        DI.set_original_sender()
    else:
        await update.message.reply_text(RebootContainer().missing_container_name())


async def cleanmemory(update, context):
    await update.message.reply_text("Executing Memory Clean...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    await Invoker.send_data_as_image(CleanMemory())
    DI.set_original_sender()


async def servershealth(update, context):
    await update.message.reply_text("Processing Servers Health stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    await Invoker.send_data_as_image(ServersHealth())
    DI.set_original_sender()


async def memory(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Processing Memory stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    await Invoker.send_data_as_image(MemoryStats())
    DI.set_original_sender()


async def cpu(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Processing CPU stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    await Invoker.send_data_as_image(CpuStats())
    DI.set_original_sender()


async def dateandlocation(update, context):
    """Send a message when the command /help is issued."""
    # u.message.reply_photo()
    await update.message.reply_text("Processing Date and Location...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    await Invoker.send_data_as_image(DateAndLocation())
    DI.set_original_sender()


async def cron(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Processing Cron Stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    await Invoker.send_data_as_image(CronStats())
    DI.set_original_sender()


async def disk(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Processing Disk Stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    await Invoker.send_data_as_image(DiskStats())
    DI.set_original_sender()


async def docker(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Processing Docker stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    await Invoker.send_data_as_image(DockerStats())
    DI.set_original_sender()


async def reports(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Processing Reports...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    await Invoker.send_server_stats_as_text()
    DI.set_original_sender()


async def echo(update, context):
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    await update.message.reply_text(f"Error : {context.error}")


def main():
    """Start the bot."""
    token = DI.get_tg_bot_token()
    application = ApplicationBuilder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("memory", memory))
    application.add_handler(CommandHandler("cpu", cpu))
    application.add_handler(CommandHandler("dateandlocation", dateandlocation))
    application.add_handler(CommandHandler("cron", cron))
    application.add_handler(CommandHandler("disk", disk))
    application.add_handler(CommandHandler("docker", docker))
    application.add_handler(CommandHandler("reports", reports))
    application.add_handler(CommandHandler("cleanmemory", cleanmemory))
    application.add_handler(CommandHandler("servershealth", servershealth))
    application.add_handler(CommandHandler("rebootapp", rebootapp))
    application.add_handler(CommandHandler("rebootcontainer", rebootcontainer))

    # on noncommand i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # log all errors
    application.add_error_handler(error)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    # updater.idle()
    application.run_polling()



if __name__ == "__main__":
    main()
