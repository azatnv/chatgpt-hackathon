import re

from dao import get_actual_events, get_week_events
from telebot import types

from utils import get_event_list_message_text


def run(bot):
    def change_page(call, events, call_data, events_on_page):
        is_brief_needed = False
        if call_data == "_events_page_":
            event_page_data = re.search(f'{call_data}(.+?)_(.+?)', call.data)
            current_page = int(event_page_data.group(1))
            is_brief_needed = int(event_page_data.group(2))
        else:
            event_page_data = re.search(f'{call_data}(.+?)', call.data)
            current_page = int(event_page_data.group(1))
        command = re.search(f'(.+?){call_data}', call.data).group(1)
        events_keyboard = call.message.reply_markup.keyboard

        if command == "next":
            if len(events) > events_on_page * (current_page + 2):
                events_next_page_button = types.InlineKeyboardButton("Далее",
                                                                     callback_data=f"next{call_data}{current_page + 1}_{is_brief_needed}")
                events_prev_page_button = types.InlineKeyboardButton("Назад",
                                                                     callback_data=f"prev{call_data}{current_page + 1}_{is_brief_needed}")
                events_curr_page_button = types.InlineKeyboardButton(f"{current_page + 2}/{len(events) // events_on_page + 1}",
                                                                     callback_data="echo")
                events_keyboard[0] = [events_prev_page_button, events_curr_page_button, events_next_page_button]
                events = events[(events_on_page * (current_page + 1)):(events_on_page * (current_page + 2))]
            else:
                events_prev_page_button = types.InlineKeyboardButton("Назад",
                                                                     callback_data=f"prev{call_data}{current_page + 1}_{is_brief_needed}")
                events_keyboard[0] = [events_prev_page_button]
                events = events[(events_on_page * (current_page + 1)):len(events)]
        else:
            if current_page > 1:
                events_next_page_button = types.InlineKeyboardButton("Далее",
                                                                     callback_data=f"next{call_data}{current_page - 1}_{is_brief_needed}")
                events_prev_page_button = types.InlineKeyboardButton("Назад",
                                                                     callback_data=f"prev{call_data}{current_page - 1}_{is_brief_needed}")
                events_curr_page_button = types.InlineKeyboardButton(f"{current_page}/{len(events) // events_on_page + 1}",
                                                                     callback_data="echo")
                events_keyboard[0] = [events_prev_page_button, events_curr_page_button, events_next_page_button]
                events = events[(events_on_page * (current_page - 1)):(events_on_page * current_page)]
            else:
                events_next_page_button = types.InlineKeyboardButton("Далее",
                                                                     callback_data=f"next{call_data}{current_page - 1}_{is_brief_needed}")
                events_keyboard[0] = [events_next_page_button]
                events = events[:events_on_page]

        return events, events_keyboard, is_brief_needed

    @bot.callback_query_handler(func=lambda call: "_events_page_" in call.data)
    async def select_page_event_query_handler(call):
        await bot.answer_callback_query(call.id)
        events = get_actual_events()
        events, events_keyboard, is_brief_needed = change_page(call, events, "_events_page_", 4)

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
        events = get_week_events()
        events, events_keyboard, _ = change_page(call, events, "_pushevents_page_", 4)

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
