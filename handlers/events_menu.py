from dao import log_action, get_actual_events, get_user_selected_comm, get_user_push_tags, \
    get_actual_events_by_topic_list
from utils import UserStates, state2pre_speech, get_event_list_message_text, filter_events_by_comm
from telebot import types


def run(bot):
    @bot.callback_query_handler(func=lambda call: "events_my" == call.data)
    async def events_full_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        log_action("events_my", call.from_user.id, call.from_user.username)

        default_state = UserStates.default
        default_state.name = "default_events_state"
        await bot.set_state(call.from_user.id, default_state, call.message.chat.id)

        is_brief_needed = False
        user_tags = get_user_push_tags(call.from_user.id)
        if len(user_tags) == 0:
            user_tags = [1, 2, 3, 4, 5, 6]
        events = get_actual_events_by_topic_list(user_tags)
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

    @bot.callback_query_handler(func=lambda call: "events_all" == call.data)
    async def events_full_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        log_action("events_all", call.from_user.id, call.from_user.username)

        default_state = UserStates.default
        default_state.name = "default_events_state"
        await bot.set_state(call.from_user.id, default_state, call.message.chat.id)

        is_brief_needed = False
        events = get_actual_events()

        events_inline_keyboard = types.InlineKeyboardMarkup()
        if len(events) > 4:
            events_next_page_button = types.InlineKeyboardButton(
                "Далее", callback_data=f"next_allevents_page_0_{1 if is_brief_needed else 0}")
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
