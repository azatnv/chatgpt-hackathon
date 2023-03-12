from telebot.async_telebot import AsyncTeleBot
import os
from dotenv import load_dotenv, find_dotenv
from main import get_events, get_communities, all_groups
from utlis import get_date_string

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
    await bot.reply_to(
        message,
        """Добро пожаловать! Я - Levart Bot, и я буду помогать тебе быть в курсе всех доступных мероприятий и ивентов! Присоединяйся и наслаждайся приключениями!"""
    )

#         post.post_url,
#         post.event_title,
#         post.event_date,
#         post.event_place,
#         post.event_short_desc,
#         post.event_picture_url


@bot.message_handler(commands=["tree_nearest_events"])
async def send_tree_nearest_events(message):
    pre_speech = "Обрадуйте себя и посетите одно из великолепных мероприятий, доступных в ближайшее время! Насладитесь прекрасными моментами, которые представляют следующие мероприятия:"
    events = get_events()
    event_list = []
    for i, event in enumerate(events, start = 1):
        post_url = event[0]
        event_title = event[1]
        event_date = get_date_string(event[2])
        event_place = f"📍 {event[3]}" if event[3] else ""
        event_short_desc = event[4]
        comm_name = event[6]
        event_text =\
            f"\n\n⚡️{comm_name} | <a href='{post_url}'>{event_title}</a>"\
            f"\n🗓 {event_date} {event_place}"\
            f"\n{event_short_desc}"
        event_list.append(event_text)
    await bot.reply_to(
        message,
        f"{pre_speech}"
        f"{''.join(event_list)}",
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@bot.message_handler(commands=["groups_info"])
async def send_groups_info(message):
    communities = all_groups
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