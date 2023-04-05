from dao import log_action, get_actual_events, get_user_selected_comm
from keyboard_buttons import menu_keyboard
from utils import UserStates, state2pre_speech, get_event_list_message_text, filter_events_by_comm
from telebot import types


def run(bot):
    @bot.callback_query_handler(func=lambda call: "events_full" == call.data)
    async def events_full_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        log_action("events_full", call.from_user.id, call.from_user.username)

        default_state = UserStates.default
        default_state.name = "default_events_state"
        await bot.set_state(call.from_user.id, default_state, call.message.chat.id)

        is_brief_needed = False
        events = get_actual_events()
        user_communities = get_user_selected_comm(call.from_user.id)
        events = filter_events_by_comm(events, user_communities)

        events_inline_keyboard = types.InlineKeyboardMarkup()
        if len(events) > 4:
            events_next_page_button = types.InlineKeyboardButton(
                "Далее", callback_data=f"next_events_page_0_{1 if is_brief_needed else 0}")
            events_inline_keyboard.add(events_next_page_button)
            events = events[:4]

        pre_speech = state2pre_speech[default_state.name]
        event_list = get_event_list_message_text(events, brief=is_brief_needed)
        await bot.send_message(
            call.message.chat.id,
            f"{pre_speech}"
            f"{''.join(event_list)}",
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=events_inline_keyboard
        )

    @bot.callback_query_handler(func=lambda call: "events_short" == call.data)
    async def events_short_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        log_action("events_short", call.from_user.id, call.from_user.username)

        default_state = UserStates.default
        default_state.name = "default_events_state"
        await bot.set_state(call.from_user.id, default_state, call.message.chat.id)

        is_brief_needed = True
        events = get_actual_events()
        user_communities = get_user_selected_comm(call.from_user.id)
        events = filter_events_by_comm(events, user_communities)

        events_inline_keyboard = types.InlineKeyboardMarkup()
        if len(events) > 6:
            events_next_page_button = types.InlineKeyboardButton(
                "Далее", callback_data=f"next_events_page_0_{1 if is_brief_needed else 0}")
            events_inline_keyboard.add(events_next_page_button)
            events = events[:6]

        pre_speech = state2pre_speech[default_state.name]
        event_list = get_event_list_message_text(events, brief=True)
        await bot.send_message(
            call.message.chat.id,
            f"{pre_speech}"
            f"{''.join(event_list)}",
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=events_inline_keyboard
        )

    @bot.callback_query_handler(func=lambda call: "events_topic" == call.data)
    async def events_topic_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        log_action("events_topic", call.from_user.id, call.from_user.username)

        await bot.send_message(
            call.message.chat.id,
            "/career - Карьера\n"
            "/education - Образование\n"
            "/sport - Спорт\n"
            "/culture_and_entertainment - Культура и развлечения\n"
            "/business - Бизнес\n"
            "/other - Другое",
            reply_markup=menu_keyboard
        )
