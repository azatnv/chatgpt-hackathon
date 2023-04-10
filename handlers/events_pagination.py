import re

from telebot.types import CallbackQuery

from dao import get_actual_events, get_actual_events_by_topic, log_action, get_user_selected_comm
from telebot import types

from utils import get_event_list_message_text, state2pre_speech, filter_events_by_comm


def run(bot):
    def change_page(call, events, call_data):
        event_page_data = re.search(f'{call_data}(.+?)_(.+?)', call.data)
        current_page = int(event_page_data.group(1))
        is_brief_needed = int(event_page_data.group(2))
        if is_brief_needed == 0:
            events_on_page = 4
        else:
            events_on_page = 6
        command = re.search(f'(.+?){call_data}', call.data).group(1)
        events_keyboard = call.message.reply_markup.keyboard

        if command == "next":
            log_action("next_event_page", call.from_user.id, call.from_user.username)
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
            log_action("prev_event_page", call.from_user.id, call.from_user.username)
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

    @bot.callback_query_handler(
        func=lambda call: "_events_page_" in call.data)
    async def select_page_event_query_handler(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        user_state: str = await bot.get_state(call.from_user.id, call.message.chat.id)
        if user_state == "default_events_state":
            events = get_actual_events()
        else:
            events = get_actual_events_by_topic(user_state)
        user_communities = get_user_selected_comm(call.from_user.id)
        events = filter_events_by_comm(events, user_communities)

        events, events_keyboard, is_brief_needed = change_page(call, events, "_events_page_")

        pre_speech = state2pre_speech[user_state]
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

    @bot.callback_query_handler(
        func=lambda call: "_allevents_page_" in call.data)
    async def select_page_event_query_handler(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        user_state: str = await bot.get_state(call.from_user.id, call.message.chat.id)
        if user_state == "default_events_state":
            events = get_actual_events()
        else:
            events = get_actual_events_by_topic(user_state)

        events, events_keyboard, is_brief_needed = change_page(call, events, "_allevents_page_")

        pre_speech = state2pre_speech[user_state]
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
