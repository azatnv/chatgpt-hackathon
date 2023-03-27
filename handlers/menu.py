from keyboard_buttons import menu_keyboard
from dao import set_user_last_date, get_actual_events, all_groups
from utils import UserStates, get_event_list_message_text
from telebot import types


def run(bot):
    @bot.message_handler(regexp=r"^Меню")
    async def menu(message):
        set_user_last_date(message.from_user.id, message.from_user.username)

        await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(
            message.chat.id,
            "Выберите опцию:",
            disable_web_page_preview=True,
            reply_markup=menu_keyboard
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

    @bot.message_handler(regexp=r"^Мероприятия")
    async def get_events(message):
        set_user_last_date(message.from_user.id, message.from_user.username, "event")

        is_brief_needed = False
        if {"кратко", "коротко", "бриф", "сводка"} & set(message.text.lower().split()):
            is_brief_needed = True

        events = get_actual_events()

        events_inline_keyboard = types.InlineKeyboardMarkup()
        current_week_events_calendar_button = types.InlineKeyboardButton("Добавить все в календарь",
                                                                         callback_data=str(
                                                                             UserStates.add_to_calendar_all))
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
