from keyboard_buttons import menu_keyboard
from dao import get_users_count


def run(bot):
    @bot.message_handler(commands=["users_count"])
    async def count_users(message):
        await bot.send_message(
            message.chat.id,
            f"Общее число пользователей: {get_users_count()}",
            reply_markup=menu_keyboard
        )
