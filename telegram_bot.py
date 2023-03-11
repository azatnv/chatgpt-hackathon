from telebot.async_telebot import AsyncTeleBot
import os
from dotenv import load_dotenv, find_dotenv
from main import get_events, get_communities


load_dotenv(find_dotenv())
#Забираем токен подключения, данные для подключения к БД
DATABASE_URL= os.environ.get('DATABASE_URL')
DATABASE_USER= os.environ.get('DATABASE_USER')
DATABASE_PASSWORD= os.environ.get('DATABASE_PASSWORD')
DATABASE_HOST= os.environ.get('DATABASE_HOST')
DATABASE_PORT= os.environ.get('DATABASE_PORT')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = AsyncTeleBot(BOT_TOKEN)



@bot.message_handler(commands=["start"])
async def send_welcome(message):
    events = get_events()
    event_list = ""
    for i, event in enumerate(events, start = 1):
        post_link = f'<a href="{event[0]}">Ссылка на пост</a>'
        event_list += f"{post_link} - {event[1]}\n"
    await bot.reply_to(
        message,
        f"Привет! Я Levart Bot. С моей помощью ты будешь в курсе всех доступных мне мероприятий и ивентов!\n"
        f"В ближайшее время доступны следующие мероприятия:\n{event_list}",
        parse_mode="HTML",
        disable_web_page_preview=False
    )


@bot.message_handler(commands=["groups_info"])
async def send_groups_info(message):
    communities = get_communities()
    communities_list = "\n".join([i[0] for i in communities])
    await bot.reply_to(
        message,
        f"На данный момент нам доступны сообщества:\n{communities_list}"
    )
    


@bot.message_handler(func=lambda msg:True)
async def echo_all(message):
    await bot.reply_to(message, message.text)


print("bot started >>> GO,GO,GO!")
import asyncio
asyncio.run(bot.polling())