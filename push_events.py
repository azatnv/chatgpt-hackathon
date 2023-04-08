import datetime
import logging
import os
import asyncio

from dotenv import load_dotenv, find_dotenv
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from dao import get_notifications_user_id_list, get_user_selected_comm, get_user_push_tags, \
    get_actual_events_by_topic_list, get_push_interval, get_next_push_date, set_next_push_date
from utils import UserStates, filter_events_by_comm, get_event_list_message_text

load_dotenv(find_dotenv())
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = AsyncTeleBot(BOT_TOKEN)

logging.getLogger('asyncio').setLevel(logging.CRITICAL)


async def push_events(user_id):
    push_interval = get_push_interval(user_id)
    next_push_date = get_next_push_date(user_id)
    if push_interval != 0 and next_push_date.date() <= datetime.date.today():
        try:
            user_tags = get_user_push_tags(user_id)
            if len(user_tags) == 0:
                user_tags = [1, 2, 3, 4, 5, 6]
            events = get_actual_events_by_topic_list(user_tags)
            user_communities = get_user_selected_comm(user_id)
            events = filter_events_by_comm(events, user_communities)

            if len(events) > 0:
                default_state = UserStates.default
                default_state.name = "default_events_state"
                await bot.set_state(user_id, user_id)

                is_brief_needed = False

                events_inline_keyboard = types.InlineKeyboardMarkup()
                if len(events) > 4:
                    events_next_page_button = types.InlineKeyboardButton(
                        "Далее", callback_data=f"next_events_page_0_{1 if is_brief_needed else 0}")
                    events_inline_keyboard.add(events_next_page_button)
                    events = events[:4]

                pre_speech = "Персональная подборка мероприятий:"
                event_list = get_event_list_message_text(events, brief=is_brief_needed)
                await bot.send_message(
                    user_id,
                    f"{pre_speech}"
                    f"{''.join(event_list)}",
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=events_inline_keyboard
                )
                set_next_push_date(user_id, datetime.datetime.now() + datetime.timedelta(push_interval))
        except:
            None


user_id_list = get_notifications_user_id_list()

for user_id in user_id_list:
    asyncio.run(push_events(user_id[0]))
