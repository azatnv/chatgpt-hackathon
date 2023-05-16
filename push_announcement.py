import logging
import os
import asyncio

from dotenv import load_dotenv, find_dotenv
from telebot.async_telebot import AsyncTeleBot

from dao import get_user_id_list, get_user_push_tags, get_notifications_user_id_list
from utils import UserStates, tag_id2text
from telebot import types

load_dotenv(find_dotenv())
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = AsyncTeleBot(BOT_TOKEN)

logging.getLogger('asyncio').setLevel(logging.CRITICAL)


# Это пуш для тех, кто еще не выполнил настройку
async def send_message(chat_id):
    await bot.set_state(chat_id, UserStates.default, chat_id)

    tags_select_buttons = list()
    user_tags = get_user_push_tags(chat_id)

    if len(user_tags) == 0:
        for tag_id in tag_id2text:
            tags_select_buttons.append(types.InlineKeyboardButton(f"✅ {tag_id2text[tag_id]}",
                                                                  callback_data=f"notifications_topic_{tag_id}"))
    else:
        for tag_id in tag_id2text:
            if tag_id in user_tags:
                tags_select_buttons.append(types.InlineKeyboardButton(f"✅ {tag_id2text[tag_id]}",
                                                                      callback_data=f"notifications_topic_{tag_id}"))
            else:
                tags_select_buttons.append(types.InlineKeyboardButton(tag_id2text[tag_id],
                                                                      callback_data=f"notifications_topic_{tag_id}"))
    notifications_topic_save_button = types.InlineKeyboardButton("Далее >",
                                                                 callback_data=f"start_save_notifications_topic")

    notifications_inline_keyboard = types.InlineKeyboardMarkup().add(*tags_select_buttons, row_width=2)
    notifications_inline_keyboard.add(notifications_topic_save_button)

    pre_speech = "Мы обновились!\n" \
                 "И я заметил, что ты до сих пор не заходил в настройки."
    try:
        await bot.send_message(
            chat_id,
            f"{pre_speech}"
        )
        await bot.send_message(
            chat_id,
            "Выберите тематики, которые Вам интересны:",
            reply_markup=notifications_inline_keyboard
        )
    except:
        pass


user_id_list = list(map(lambda x: x[0], get_user_id_list()))
notifications_user_id_list = list(map(lambda x: x[0], get_notifications_user_id_list()))
users_without_settings = list(set(user_id_list) - set(notifications_user_id_list))

for user_id in users_without_settings:
    asyncio.run(send_message(user_id))
