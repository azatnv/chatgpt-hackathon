import re
import os

from telebot import types
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv, find_dotenv

from inline_buttons import init_keyboard
from inline_buttons.inline_buttons import link_to_menu_keyboard, menu_keyboard
from main import get_tree_nearest_events, all_groups, get_current_week_events, get_next_week_events, \
    set_suggested_event_source, set_suggested_functionality
from utils import get_date_string, UserStates

load_dotenv(find_dotenv())
#  Забираем токен подключения, данные для подключения к БД
DATABASE_URL= os.environ.get('DATABASE_URL')
DATABASE_USER= os.environ.get('DATABASE_USER')
DATABASE_PASSWORD= os.environ.get('DATABASE_PASSWORD')
DATABASE_HOST= os.environ.get('DATABASE_HOST')
DATABASE_PORT= os.environ.get('DATABASE_PORT')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = AsyncTeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.send_message(
        message.chat.id,
        """
        Добро пожаловать! 

Я собираю ближайшие мероприятия ИТМО и отдаю краткую сводку, которую ты сможешь изучить за 3 минуты. 

Больше не нужно самим искать «то самое мероприятие» и тратить свое время.

Просто попробуй.""",
        reply_markup = init_keyboard
    )


@bot.message_handler(regexp=r"^Меню")
async def menu(message: types.Message):
    await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.send_message(
        message.chat.id,
        "Выберите опцию:",
        disable_web_page_preview=True,
        reply_markup=menu_keyboard
    )


@bot.message_handler(regexp=r"^Ближайшие мероприятия")
async def send_tree_nearest_events(message):
    nearest_events_inline_keyboard = types.InlineKeyboardMarkup()
    nearest_events_calendar_button = types.InlineKeyboardButton("Добавить в календарь", callback_data=str(UserStates.calendar_nearest_events))
    menu_inline_button = types.InlineKeyboardButton("Меню", callback_data=str(UserStates.default))
    nearest_events_inline_keyboard.add(nearest_events_calendar_button).add(menu_inline_button)

    pre_speech = "Levart подобрал анонсы самых ближайших мероприятий:"
    events = get_tree_nearest_events()
    event_list = []
    for i, event in enumerate(events, start=1):
        post_url = event[0]
        event_title = event[1]
        event_date = get_date_string(event[2])
        event_place = f"📍 {event[3]}" if event[3] else ""
        event_short_desc = event[4]
        comm_name = event[6]
        event_text = \
            f"\n\n⚡️{comm_name} | <a href='{post_url}'>{event_title}</a>" \
            f"\n🗓 {event_date} {event_place}" \
            f"\n{event_short_desc}"
        event_list.append(event_text)
    await bot.send_message(
        message.chat.id,
        f"{pre_speech}"
        f"{''.join(event_list)}",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=nearest_events_inline_keyboard
    )


@bot.message_handler(regexp=r"^Текущая неделя")
async def current_week_events(message):
    pre_speech = "Анонсы мероприятий на ТЕКУЩУЮ неделю:"
    events = get_current_week_events()
    event_list = []
    for i, event in enumerate(events, start=1):
        post_url = event[0]
        event_title = event[1]
        event_date = get_date_string(event[2])
        event_place = f"📍 {event[3]}" if event[3] else ""
        event_short_desc = event[4]
        comm_name = event[6]
        event_text = \
            f"\n\n⚡️{comm_name} | <a href='{post_url}'>{event_title}</a>" \
            f"\n🗓 {event_date} {event_place}" \
            f"\n{event_short_desc}"
        event_list.append(event_text)
    await bot.send_message(
        message.chat.id,
        f"{pre_speech}"
        f"{''.join(event_list)}",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=link_to_menu_keyboard
    )


@bot.message_handler(regexp=r"^Следующая неделя")
async def next_week_events(message):
    pre_speech = "Анонсы мероприятий на СЛЕДУЮЩУЮ неделю:"
    events = get_next_week_events()
    event_list = []
    for i, event in enumerate(events, start=1):
        post_url = event[0]
        event_title = event[1]
        event_date = get_date_string(event[2])
        event_place = f"📍 {event[3]}" if event[3] else ""
        event_short_desc = event[4]
        comm_name = event[6]
        event_text = \
            f"\n\n⚡️{comm_name} | <a href='{post_url}'>{event_title}</a>" \
            f"\n🗓 {event_date} {event_place}" \
            f"\n{event_short_desc}"
        event_list.append(event_text)
    await bot.send_message(
        message.chat.id,
        f"{pre_speech}"
        f"{''.join(event_list)}",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=link_to_menu_keyboard
    )


@bot.message_handler(regexp=r"^Источники мероприятий")
async def send_groups_info(message):
    communities = all_groups
    communities_list = []
    for i in communities:
        communities_text = f" 🌐 {i[0]}"
        communities_list.append(communities_text)
    communities_text = "\n".join(communities_list)
    await bot.send_message(
        message.chat.id,
        f"На данный момент нам доступны сообщества:\n\n{communities_text}",
        disable_web_page_preview=True,
        reply_markup=link_to_menu_keyboard
    )


@bot.message_handler(regexp=r"^Предложить улучшение")
async def suggest_improvement(message):
    suggest_menu_inline_keyboard = types.InlineKeyboardMarkup()
    suggest_event_source_button = types.InlineKeyboardButton("Посоветовать источник", callback_data=str(UserStates.suggest_source))
    suggest_functionality_button = types.InlineKeyboardButton("Посоветовать функционал", callback_data=str(UserStates.suggest_functionality))
    menu_inline_button = types.InlineKeyboardButton("Меню", callback_data=str(UserStates.default))
    suggest_menu_inline_keyboard.add(suggest_event_source_button, suggest_functionality_button, menu_inline_button, row_width=1)
    await bot.send_message(
        message.chat.id,
        "Подскажите, как нам стать лучше:",
        disable_web_page_preview=True,
        reply_markup=suggest_menu_inline_keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data == str(UserStates.default))
async def menu_query_handler(call):
    await bot.set_state(call.from_user.id, UserStates.default, call.message.chat.id)
    await bot.answer_callback_query(call.id)
    await bot.send_message(
        call.message.chat.id,
        "Меню:",
        disable_web_page_preview=True,
        reply_markup=menu_keyboard
    )


@bot.callback_query_handler(func=lambda call: "suggest_" in call.data)
async def suggest_query_handler(call):
    if call.data == str(UserStates.suggest_source):
        await bot.answer_callback_query(
            call.id,
            "Отправьте ссылку на источник"
        )
        await bot.send_message(
            call.message.chat.id,
            "Отправьте ссылку на источник с мероприятиями:"
        )
        await bot.set_state(call.from_user.id, UserStates.suggest_source, call.message.chat.id)
    if call.data == str(UserStates.suggest_functionality):
        await bot.answer_callback_query(
            call.id,
            "Предложите функционал"
        )
        await bot.send_message(
            call.message.chat.id,
            "Какие функции хотелось бы видеть в будущем?"
        )
        await bot.set_state(call.from_user.id, UserStates.suggest_functionality, call.message.chat.id)


@bot.callback_query_handler(func=lambda call: "calendar_" in call.data)
async def calendar_query_handler(call):
    if call.data == str(UserStates.calendar_nearest_events):
        button_list = [
            types.InlineKeyboardButton("1", callback_data="select_event_to_cal_0"),
            types.InlineKeyboardButton("2", callback_data="select_event_to_cal_1"),
            types.InlineKeyboardButton("3", callback_data="select_event_to_cal_2")
        ]
        events_keyboard = types.InlineKeyboardMarkup().add(*button_list, row_width=1)
        events_keyboard.row(types.InlineKeyboardButton("Добавить", callback_data=str(UserStates.calendar_nearest_events_add)),
                            types.InlineKeyboardButton("Меню", callback_data=str(UserStates.default)))

        await bot.set_state(call.from_user.id, UserStates.default, call.message.chat.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(
            call.message.chat.id,
            "Отметьте мероприятия, которые необходимо добавить:",
            disable_web_page_preview=True,
            reply_markup=events_keyboard
        )
    if call.data == str(UserStates.calendar_nearest_events_add):
        print("calendar_nearest_events_add")


@bot.callback_query_handler(func=lambda call: "select_event_to_cal_" in call.data)
async def select_event_calendar_query_handler(call):
    await bot.answer_callback_query(call.id)
    selected_button_n = int(call.data.replace("select_event_to_cal_", ""))
    events_keyboard = call.message.reply_markup.keyboard
    selected_button_text = events_keyboard[selected_button_n][0].text
    if "✅" in selected_button_text:
        new_button_text = selected_button_text.replace(" ✅", "")
    else:
        new_button_text = selected_button_text + " ✅"
    events_keyboard[selected_button_n][0].text = new_button_text
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                        reply_markup=types.InlineKeyboardMarkup(events_keyboard))


@bot.message_handler()
async def echo_all(message: types.Message):
    user_state = await bot.get_state(message.from_user.id, message.chat.id)
    user_id = message.from_user.id
    username = message.from_user.username
    user_message_text = message.text
    if str(user_state) == str(UserStates.suggest_source):
        if user_message_text.startswith("http"):
            user_url_message_modified = user_message_text
        else:
            user_url_message_modified = "http://" + user_message_text
        regex = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?)' #domain
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if regex.search(user_url_message_modified):
            await bot.set_state(user_id, UserStates.default, message.chat.id)
            await bot.send_message(
                message.chat.id,
                "Ваше предложение принято!",
                disable_web_page_preview=True,
                reply_markup=link_to_menu_keyboard
            )
            set_suggested_event_source(user_id, username, user_message_text)
        else:
            await bot.send_message(
                message.chat.id,
                "Введите корректную ссылку"
            )
    elif str(user_state) == str(UserStates.suggest_functionality):
        await bot.set_state(user_id, UserStates.default, message.chat.id)
        await bot.send_message(
            message.chat.id,
            "Спасибо за советы! Мы обязательно рассмотрим твое предложение и подумаем как можно сделать бота еще лучше",
            disable_web_page_preview=True,
            reply_markup=link_to_menu_keyboard
        )
        set_suggested_functionality(user_id, username, user_message_text)
    else:
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(
            message.chat.id,
            "Меню:",
            disable_web_page_preview=True,
            reply_markup=link_to_menu_keyboard
        )


print("bot started >>> GO,GO,GO!")
import asyncio
asyncio.run(bot.polling())