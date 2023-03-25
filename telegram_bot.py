import importlib
import os

from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = AsyncTeleBot(BOT_TOKEN)

for x in os.listdir("handlers/"):
    if x.endswith(".py"):
        handler = importlib.import_module("handlers." + x[:-3])
        handler.run(bot)

print("bot started >>> GO,GO,GO!")

import asyncio
asyncio.run(bot.polling())
