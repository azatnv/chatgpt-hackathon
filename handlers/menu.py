from keyboard_buttons import menu_keyboard
from dao import set_user_last_date, all_groups, log_action, get_actual_events_by_topic
from utils import UserStates, get_event_list_message_text, state2pre_speech
from telebot import types


def run(bot):
    @bot.message_handler(regexp="^Мероприятия")
    async def get_events(message):
        set_user_last_date(message.from_user.id, message.from_user.username, "event")
        await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
        log_action("event_button", message.from_user.id, message.from_user.username)

        events_full_button = types.InlineKeyboardButton("Подробно", callback_data="events_full")
        events_short_button = types.InlineKeyboardButton("Кратко", callback_data="events_short")
        events_topic_button = types.InlineKeyboardButton("По категориям", callback_data="events_topic")
        events_calendar_button = types.InlineKeyboardButton("Добавить все в календарь",
                                                            callback_data=str(UserStates.add_to_calendar_all))
        events_inline_keyboard = types.InlineKeyboardMarkup().add(events_full_button, events_short_button,
                                                                  events_topic_button, events_calendar_button,
                                                                  row_width=2)

        await bot.send_message(
            message.chat.id,
            "Мероприятия:",
            reply_markup=events_inline_keyboard
        )

    @bot.message_handler(commands=["career", "education", "sport", "culture_and_entertainment", "business", "other"])
    async def get_events_by_topic(message):
        await bot.delete_message(message.chat.id, message.message_id)
        set_user_last_date(message.from_user.id, message.from_user.username, "event")
        topic_state = UserStates.topic
        topic_state.name = message.text.replace("/", "")
        await bot.set_state(message.from_user.id, topic_state, message.chat.id)
        log_action("topic_command", message.from_user.id, message.from_user.username)

        is_brief_needed = False
        if {"кратко", "коротко", "бриф", "сводка"} & set(message.text.lower().split()):
            is_brief_needed = True

        events = get_actual_events_by_topic(topic_state.name)

        events_inline_keyboard = types.InlineKeyboardMarkup()
        if len(events) > 4:
            events_next_page_button = types.InlineKeyboardButton("Далее",
                                                                 callback_data=f"next_events_page_0_{1 if is_brief_needed else 0}")
            events_inline_keyboard.add(events_next_page_button)
            events = events[:4]

        pre_speech = state2pre_speech[topic_state.name]
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
        await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
        log_action("community_button", message.from_user.id, message.from_user.username)

        communities = all_groups
        communities_list = {"vk": [], "tg": []}
        for i in communities:
            if i[3]:
                communities_list["tg"].append(f" 🌐 {i[0]}")
            else:
                communities_list["vk"].append(f" 🌐 {i[0]}")
        communities_text = "Вконтакте:\n"
        communities_text += "\n".join(communities_list["vk"])
        communities_text += "\n\nTelegram:\n"
        communities_text += "\n".join(communities_list["tg"])
        await bot.send_message(
            message.chat.id,
            f"На данный момент нам доступны сообщества:\n\n{communities_text}",
            disable_web_page_preview=True,
            reply_markup=menu_keyboard
        )

    @bot.message_handler(regexp=r"^Предложить улучшение")
    async def suggest_improvement(message):
        set_user_last_date(message.from_user.id, message.from_user.username)
        await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
        log_action("suggest_button", message.from_user.id, message.from_user.username)

        suggest_menu_inline_keyboard = types.InlineKeyboardMarkup()
        suggest_event_source_button = types.InlineKeyboardButton("Посоветовать источник",
                                                                 callback_data=str(UserStates.suggest_source))
        suggest_functionality_button = types.InlineKeyboardButton("Посоветовать функционал",
                                                                  callback_data=str(UserStates.suggest_functionality))
        suggest_menu_inline_keyboard.add(suggest_event_source_button, suggest_functionality_button, row_width=1)
        await bot.send_message(
            message.chat.id,
            "Подскажите, как нам стать лучше:",
            disable_web_page_preview=True,
            reply_markup=suggest_menu_inline_keyboard
        )
