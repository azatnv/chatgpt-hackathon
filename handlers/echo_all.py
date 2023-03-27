import re

from keyboard_buttons import menu_keyboard
from dao import set_suggested_event_source, set_suggested_functionality
from utils import UserStates


def run(bot):
    @bot.message_handler(func=lambda message: message.text not in ["/start", "/users_count", "Меню", "Мероприятия",
                                                                   "Источники мероприятий", "Предложить улучшение"])
    async def echo_all(message):
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
