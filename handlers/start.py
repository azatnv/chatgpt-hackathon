from inline_buttons import init_keyboard
from dao import set_user_start_date, log_action
from keyboard_buttons import init_keyboard
from dao import set_user_start_date
from utils import UserStates


def run(bot):
    @bot.message_handler(commands=["start"])
    async def send_welcome(message):
        set_user_start_date(message.from_user.id, message.from_user.username)
        log_action("start", message.from_user.id, message.from_user.username)

        await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.send_message(
            message.chat.id,
            """
            🇷🇺 Добро пожаловать! 

С этого момента все мероприятия с тобой в удобной форме.

Наши партнеры: [Napoleon IT](https://www.napoleonit.com/)


🇬🇧 Good to see you!
            
All the ITMO events are now consolidated with us, making it more convenient for you.

Partners: [Napoleon IT](https://www.napoleonit.com/)""",
            reply_markup=init_keyboard,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
