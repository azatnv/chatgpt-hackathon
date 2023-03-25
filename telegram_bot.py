import re
import os
import tempfile

from icalendar import Calendar, Event, vText
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv, find_dotenv

from inline_buttons import init_keyboard
from inline_buttons.inline_buttons import menu_keyboard
from main import all_groups, set_suggested_event_source, set_suggested_functionality, \
    set_user_start_date, set_user_last_date, get_users_count, get_actual_events, get_week_events
from utils import get_date_string, UserStates, make_google_cal_url

load_dotenv(find_dotenv())
#  Забираем токен подключения, данные для подключения к БД
DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_PORT = os.environ.get('DATABASE_PORT')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = AsyncTeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    set_user_start_date(message.from_user.id, message.from_user.username)

    await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.send_message(
        message.chat.id,
        """
        Добро пожаловать! 

С этого момента все мероприятия с тобой в удобной форме.

Наши партнеры: [Gigaschool](https://gigaschool.ru/)""",
        reply_markup=init_keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


@bot.message_handler(commands=["users_count"])
async def count_users(message: types.Message):
    await bot.send_message(
        message.chat.id,
        f"Общее число пользователей: {get_users_count()}",
        reply_markup=menu_keyboard
    )


@bot.message_handler(regexp=r"^Меню")
async def menu(message: types.Message):
    set_user_last_date(message.from_user.id, message.from_user.username)

    await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.send_message(
        message.chat.id,
        "Выберите опцию:",
        disable_web_page_preview=True,
        reply_markup=menu_keyboard
    )


def get_event_list_message_text(events, brief=False):
    event_list = []
    for i, event in enumerate(events, start=1):
        post_url = event[0]
        event_title = event[1]
        event_date = get_date_string(event[2])
        event_place = ""
        if event[3]:
            if "онлайн" in event[3].lower() or "online" in event[3].lower():
                event_place = f"📍 онлайн"
            else:
                event_place = f"📍 оффлайн"
        event_short_desc = event[4]
        comm_name = event[6]
        event_date_link = make_google_cal_url(event_title, event[2], event[3] if event[3] else "", comm_name,
                                              event_short_desc, post_url)
        if not brief:
            event_text = \
                f"\n\n🦄️ <a href='{post_url}'>{event_title}</a>" \
                f"\n🗓 {event_date} {event_place}" \
                f"\n{event_short_desc}"\
                f"\n<a href='{event_date_link}'>Добавить в календарь -></a>"
        else:
            event_text = f"\n\n🗓 {event_date} {event_place} - 🦄️ <a href='{post_url}'>{event_title}</a>"
        event_list.append(event_text)
    return event_list


@bot.message_handler(regexp=r"^Мероприятия")
async def get_events(message):
    set_user_last_date(message.from_user.id, message.from_user.username, "event")

    events = get_actual_events()

    is_brief_needed = False
    if {"кратко", "коротко", "бриф", "сводка"} & set(message.text.lower().split()):
        is_brief_needed = True

    events_inline_keyboard = types.InlineKeyboardMarkup()
    current_week_events_calendar_button = types.InlineKeyboardButton("Добавить все в календарь",
                                                                     callback_data=str(UserStates.add_to_calendar_all))
    menu_inline_button = types.InlineKeyboardButton("Меню", callback_data=str(UserStates.default))
    if len(events) > 4:
        events_next_page_button = types.InlineKeyboardButton("Далее", callback_data=f"next_events_page_0_{1 if is_brief_needed else 0}")
        events_inline_keyboard.add(events_next_page_button)
        events = events[:4]
    events_inline_keyboard.add(current_week_events_calendar_button, menu_inline_button, row_width=1)

    pre_speech = "Анонсы мероприятий:"
    event_list = get_event_list_message_text(events, brief=is_brief_needed)
    await bot.send_message(
        message.chat.id,
        f"{pre_speech}"
        f"{''.join(event_list)}",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=events_inline_keyboard
    )


@bot.message_handler(regexp=r"^Источники мероприятий")
async def send_groups_info(message):
    set_user_last_date(message.from_user.id, message.from_user.username, "community")

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
        reply_markup=menu_keyboard
    )


@bot.message_handler(regexp=r"^Предложить улучшение")
async def suggest_improvement(message):
    set_user_last_date(message.from_user.id, message.from_user.username)

    suggest_menu_inline_keyboard = types.InlineKeyboardMarkup()
    suggest_event_source_button = types.InlineKeyboardButton("Посоветовать источник",
                                                             callback_data=str(UserStates.suggest_source))
    suggest_functionality_button = types.InlineKeyboardButton("Посоветовать функционал",
                                                              callback_data=str(UserStates.suggest_functionality))
    menu_inline_button = types.InlineKeyboardButton("Меню", callback_data=str(UserStates.default))
    suggest_menu_inline_keyboard.add(suggest_event_source_button, suggest_functionality_button, menu_inline_button,
                                     row_width=1)
    await bot.send_message(
        message.chat.id,
        "Подскажите, как нам стать лучше:",
        disable_web_page_preview=True,
        reply_markup=suggest_menu_inline_keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data == str(UserStates.default))
async def menu_query_handler(call):
    await bot.set_state(call.from_user.id, UserStates.default, call.message.chat.id)
    await bot.delete_message(call.message.chat.id, call.message.message_id)
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


async def add_to_calendar(events, call):
    set_user_last_date(call.from_user.id, call.from_user.username, "calendar")

    event_list_add = list()
    for event in events:
        post_url = event[0]
        event_title = event[1]
        event_date = event[2]
        event_place = event[3] if event[3] else ""
        event_short_desc = event[4]
        comm_name = event[6]
        event_list_add.append([event_title, event_date, event_place,
                               comm_name + "\n\n" + event_short_desc + "\n\n" + post_url])

    cal = Calendar()
    cal.add("prodid", "-//Levart//levart_bot//")
    cal.add("version", "2.0")
    cal.add("name", "Мероприятия от levart")
    cal.add("timezone", "Europe/Moscow")
    for event in event_list_add:
        cal_event = Event()
        cal_event.add('summary', event[0])
        cal_event.add('dtstart', event[1])
        cal_event.add('location', vText(event[2]))
        cal_event.add('description', event[3])
        cal.add_component(cal_event)
    await bot.answer_callback_query(
        call.id,
        "Мероприятия добавлены"
    )
    await bot.send_message(
        call.message.chat.id,
        "Загрузите файл ICS, чтобы добавить в календарь.\n"
        "Также можно добавить каждое мероприятие отдельно, нажав на ссылки в сообщении.",
        disable_web_page_preview=True,
        reply_markup=menu_keyboard
    )
    directory = tempfile.mkdtemp()
    f = open(os.path.join(directory, f'Мероприятия - {call.from_user.username}.ics'), 'wb+')
    f.write(cal.to_ical())
    f.close()
    with open(os.path.join(directory, f'Мероприятия - {call.from_user.username}.ics'), 'rb') as f:
        await bot.send_document(call.message.chat.id, f)
    f.close()


@bot.callback_query_handler(func=lambda call: call.data == str(UserStates.add_to_calendar_all))
async def add_to_calendar_all(call):
    events = get_actual_events()
    await add_to_calendar(events, call)


@bot.callback_query_handler(func=lambda call: call.data == str(UserStates.add_to_calendar_week))
async def add_to_calendar_week(call):
    events = get_week_events()
    await add_to_calendar(events, call)


@bot.callback_query_handler(func=lambda call: "_events_page_" in call.data)
async def select_page_event_query_handler(call):
    await bot.answer_callback_query(call.id)
    event_page_data = re.search('_events_page_(.+?)_(.+?)', call.data)
    current_page = int(event_page_data.group(1))
    is_brief_needed = int(event_page_data.group(2))
    command = re.search('(.+?)_events_page_', call.data).group(1)
    events_keyboard = call.message.reply_markup.keyboard
    events = get_actual_events()
    if command == "next":
        if len(events) > 4 * (current_page + 2):
            events_next_page_button = types.InlineKeyboardButton("Далее",
                                                                 callback_data=f"next_events_page_{current_page + 1}_{is_brief_needed}")
            events_prev_page_button = types.InlineKeyboardButton("Назад",
                                                                 callback_data=f"prev_events_page_{current_page + 1}_{is_brief_needed}")
            events_curr_page_button = types.InlineKeyboardButton(f"{current_page + 2}/{len(events) // 4 + 1}",
                                                                 callback_data="echo")
            events_keyboard[0] = [events_prev_page_button, events_curr_page_button, events_next_page_button]
            events = events[(4 * (current_page + 1)):(4 * (current_page + 2))]
        else:
            events_prev_page_button = types.InlineKeyboardButton("Назад",
                                                                 callback_data=f"prev_events_page_{current_page + 1}_{is_brief_needed}")
            events_keyboard[0] = [events_prev_page_button]
            events = events[(4 * (current_page + 1)):len(events)]
    else:
        if current_page > 1:
            events_next_page_button = types.InlineKeyboardButton("Далее",
                                                                 callback_data=f"next_events_page_{current_page - 1}_{is_brief_needed}")
            events_prev_page_button = types.InlineKeyboardButton("Назад",
                                                                 callback_data=f"prev_events_page_{current_page - 1}_{is_brief_needed}")
            events_curr_page_button = types.InlineKeyboardButton(f"{current_page}/{len(events) // 4 + 1}",
                                                                 callback_data="echo")
            events_keyboard[0] = [events_prev_page_button, events_curr_page_button, events_next_page_button]
            events = events[(4 * (current_page - 1)):(4 * current_page)]
        else:
            events_next_page_button = types.InlineKeyboardButton("Далее",
                                                                 callback_data=f"next_events_page_{current_page - 1}_{is_brief_needed}")
            events_keyboard[0] = [events_next_page_button]
            events = events[:4]

    pre_speech = "Анонсы мероприятий:"
    event_list = get_event_list_message_text(events, brief=bool(is_brief_needed))

    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.send_message(
        call.message.chat.id,
        f"{pre_speech}"
        f"{''.join(event_list)}",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=types.InlineKeyboardMarkup(events_keyboard)
    )


@bot.callback_query_handler(func=lambda call: "_pushevents_page_" in call.data)
async def select_push_page_event_query_handler(call):
    await bot.answer_callback_query(call.id)
    current_page = int(re.search('_pushevents_page_(.+?)', call.data).group(1))
    command = re.search('(.+?)_pushevents_page_', call.data).group(1)
    events_keyboard = call.message.reply_markup.keyboard
    events = get_week_events()
    if command == "next":
        if len(events) > 4 * (current_page + 2):
            events_next_page_button = types.InlineKeyboardButton("Далее",
                                                                 callback_data=f"next_pushevents_page_{current_page + 1}")
            events_prev_page_button = types.InlineKeyboardButton("Назад",
                                                                 callback_data=f"prev_pushevents_page_{current_page + 1}")
            events_curr_page_button = types.InlineKeyboardButton(f"{current_page + 2}/{len(events)//4+1}", callback_data="echo")
            events_keyboard[0] = [events_prev_page_button, events_curr_page_button, events_next_page_button]
            events = events[(4 * (current_page + 1)):(4 * (current_page + 2))]
        else:
            events_prev_page_button = types.InlineKeyboardButton("Назад",
                                                                 callback_data=f"prev_pushevents_page_{current_page + 1}")
            events_keyboard[0] = [events_prev_page_button]
            events = events[(4 * (current_page + 1)):len(events)]
    else:
        if current_page > 1:
            events_next_page_button = types.InlineKeyboardButton("Далее",
                                                                 callback_data=f"next_pushevents_page_{current_page - 1}")
            events_prev_page_button = types.InlineKeyboardButton("Назад",
                                                                 callback_data=f"prev_pushevents_page_{current_page - 1}")
            events_curr_page_button = types.InlineKeyboardButton(f"{current_page}/{len(events)//4+1}", callback_data="echo")
            events_keyboard[0] = [events_prev_page_button, events_curr_page_button, events_next_page_button]
            events = events[(4 * (current_page - 1)):(4 * current_page)]
        else:
            events_next_page_button = types.InlineKeyboardButton("Далее",
                                                                 callback_data=f"next_pushevents_page_{current_page - 1}")
            events_keyboard[0] = [events_next_page_button]
            events = events[:4]

    pre_speech = "Я подготовил для тебя мероприятия на ближайшую неделю:"
    event_list = get_event_list_message_text(events)

    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await bot.send_message(
        call.message.chat.id,
        f"{pre_speech}"
        f"{''.join(event_list)}",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=types.InlineKeyboardMarkup(events_keyboard)
    )


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
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?)'  # domain
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if regex.search(user_url_message_modified):
            await bot.set_state(user_id, UserStates.default, message.chat.id)
            await bot.send_message(
                message.chat.id,
                "Ваше предложение принято!",
                disable_web_page_preview=True,
                reply_markup=menu_keyboard
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
            reply_markup=menu_keyboard
        )
        set_suggested_functionality(user_id, username, user_message_text)
    else:
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(
            message.chat.id,
            "Меню:",
            disable_web_page_preview=True,
            reply_markup=menu_keyboard
        )


print("bot started >>> GO,GO,GO!")
import asyncio

asyncio.run(bot.polling())
