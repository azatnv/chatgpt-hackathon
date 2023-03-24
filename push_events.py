import logging
import os
import asyncio

from dotenv import load_dotenv, find_dotenv
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from main import get_week_events, get_user_id_list
from utils import UserStates, get_date_string, make_google_cal_url

load_dotenv(find_dotenv())
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = AsyncTeleBot(BOT_TOKEN)

logging.getLogger('asyncio').setLevel(logging.CRITICAL)


def get_event_list_message_text(events):
    event_list = []
    for i, event in enumerate(events, start=1):
        post_url = event[0]
        event_title = event[1]
        event_date = get_date_string(event[2])
        event_place = f"📍 {event[3]}" if event[3] else ""
        event_short_desc = event[4]
        comm_name = event[6]
        event_date_link = make_google_cal_url(event_title, event[2], event[3] if event[3] else "", comm_name,
                                              event_short_desc, post_url)
        event_text = \
            f"\n\n⚡️{comm_name} | <a href='{post_url}'>{event_title}</a>" \
            f"\n🗓 <a href='{event_date_link}'>{event_date}</a> {event_place}" \
            f"\n{event_short_desc}"
        event_list.append(event_text)
    return event_list


def get_week_events_text():
    events = get_week_events()

    events_inline_keyboard = types.InlineKeyboardMarkup()
    current_week_events_calendar_button = types.InlineKeyboardButton("Добавить все в календарь",
                                                                     callback_data=str(UserStates.add_to_calendar_week))
    menu_inline_button = types.InlineKeyboardButton("Меню", callback_data=str(UserStates.default))
    if len(events) > 4:
        events_next_page_button = types.InlineKeyboardButton("Далее", callback_data="next_pushevents_page_0")
        events_inline_keyboard.add(events_next_page_button)
        events = events[:4]
    events_inline_keyboard.add(current_week_events_calendar_button, menu_inline_button, row_width=1)

    event_list = get_event_list_message_text(events)

    return event_list, events_inline_keyboard


event_list, events_inline_keyboard = get_week_events_text()


async def push_events(chat_id):
    pre_speech = "Я подготовил для тебя мероприятия на ближайшую неделю:"
    try:
        await bot.send_message(
            chat_id,
            f"{pre_speech}"
            f"{''.join(event_list)}",
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=events_inline_keyboard
        )
    except:
        None

user_id_list = get_user_id_list()

for user_id in user_id_list:
    asyncio.run(push_events(user_id[0]))
