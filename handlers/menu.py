from keyboard_buttons import menu_keyboard
from dao import all_groups, log_action, get_actual_events_by_topic, get_user_selected_comm, get_actual_events, \
    get_user_push_tags, get_actual_events_by_topic_list
from utils import UserStates, get_event_list_message_text, state2pre_speech, filter_events_by_comm, command2topic
from telebot import types


def run(bot):
    @bot.message_handler(regexp="^Мероприятия 👀")
    async def get_events(message):
        await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
        log_action("event_button", message.from_user.id, message.from_user.username)

        events_all_button = types.InlineKeyboardButton("Мои мероприятия 👀", callback_data="events_my")
        events_my_button = types.InlineKeyboardButton("Все мероприятия 🗂", callback_data="events_all")
        events_cancel_button = types.InlineKeyboardButton("< В меню", callback_data="settings_cancel")

        events_inline_keyboard = types.InlineKeyboardMarkup().add(events_all_button, events_my_button,
                                                                  events_cancel_button, row_width=1)

        await bot.send_message(
            message.chat.id,
            "В каком формате смотрим? 🤔",
            reply_markup=events_inline_keyboard
        )

    @bot.message_handler(commands=["career", "edu", "sport", "fun", "money", "other"])
    async def get_events_by_topic(message):
        await bot.delete_message(message.chat.id, message.message_id)
        topic_state = UserStates.topic
        topic_state.name = command2topic[message.text]
        await bot.set_state(message.from_user.id, topic_state, message.chat.id)
        log_action("topic_command", message.from_user.id, message.from_user.username)

        is_brief_needed = False
        if {"кратко", "коротко", "бриф", "сводка"} & set(message.text.lower().split()):
            is_brief_needed = True

        events = get_actual_events_by_topic(topic_state.name)
        user_communities = get_user_selected_comm(message.from_user.id)
        events = filter_events_by_comm(events, user_communities)

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

    @bot.message_handler(commands=["all"])
    async def get_events_all(message):
        await bot.delete_message(message.chat.id, message.message_id)

        log_action("events_all", message.from_user.id, message.from_user.username)

        default_state = UserStates.default
        default_state.name = "default_events_state"
        await bot.set_state(message.from_user.id, default_state, message.chat.id)

        is_brief_needed = False
        events = get_actual_events()
        user_communities = get_user_selected_comm(message.from_user.id)
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
            message.chat.id,
            f"{pre_speech}"
            f"{''.join(event_list)}",
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=events_inline_keyboard
        )

    @bot.message_handler(commands=["brief"])
    async def get_events_brief(message):
        await bot.delete_message(message.chat.id, message.message_id)

        log_action("events_brief", message.from_user.id, message.from_user.username)

        default_state = UserStates.default
        default_state.name = "default_events_state"
        await bot.set_state(message.from_user.id, default_state, message.chat.id)

        is_brief_needed = True
        user_tags = get_user_push_tags(message.from_user.id)
        if len(user_tags) == 0:
            user_tags = [1, 2, 3, 4, 5, 6]
        events = get_actual_events_by_topic_list(user_tags)
        user_communities = get_user_selected_comm(message.from_user.id)
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
            message.chat.id,
            f"{pre_speech}"
            f"{''.join(event_list)}",
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=events_inline_keyboard
        )

    @bot.message_handler(regexp=r"^Источники мероприятий")
    async def send_groups_info(message):
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

    @bot.message_handler(regexp="^Настройки ⚙️")
    async def get_settings(message):
        await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
        log_action("settings_button", message.from_user.id, message.from_user.username)

        notifications_schedule_button = types.InlineKeyboardButton("Уведомления 🔔",
                                                                   callback_data="notifications_schedule")
        notifications_topic_button = types.InlineKeyboardButton("Тематики 🗂",
                                                                callback_data="notifications_topic")
        settings_communities_button = types.InlineKeyboardButton("Источники мероприятий 📚",
                                                                 callback_data="settings_communities")
        commands_info_button = types.InlineKeyboardButton("Посмотреть команды бота ℹ️",
                                                          callback_data="commands_info")
        settings_cancel_button = types.InlineKeyboardButton("< В меню",
                                                            callback_data="settings_cancel")

        settings_inline_keyboard = types.InlineKeyboardMarkup().add(notifications_schedule_button,
                                                                    notifications_topic_button,
                                                                    settings_communities_button,
                                                                    commands_info_button,
                                                                    settings_cancel_button, row_width=1)
        await bot.send_message(
            message.chat.id,
            "Настройки:",
            reply_markup=settings_inline_keyboard
        )

    @bot.callback_query_handler(func=lambda call: "back_to_settings" == call.data)
    async def back_to_settings_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        notifications_schedule_button = types.InlineKeyboardButton("Уведомления 🔔",
                                                                   callback_data="notifications_schedule")
        notifications_topic_button = types.InlineKeyboardButton("Тематики 🗂",
                                                                callback_data="notifications_topic")
        settings_communities_button = types.InlineKeyboardButton("Источники мероприятий 📚",
                                                                 callback_data="settings_communities")
        commands_info_button = types.InlineKeyboardButton("Посмотреть команды бота ℹ️",
                                                          callback_data="commands_info")
        settings_cancel_button = types.InlineKeyboardButton("< В меню",
                                                            callback_data="settings_cancel")

        settings_inline_keyboard = types.InlineKeyboardMarkup().add(notifications_schedule_button,
                                                                    notifications_topic_button,
                                                                    settings_communities_button,
                                                                    commands_info_button,
                                                                    settings_cancel_button, row_width=1)
        await bot.send_message(
            call.message.chat.id,
            "Настройки:",
            reply_markup=settings_inline_keyboard
        )
