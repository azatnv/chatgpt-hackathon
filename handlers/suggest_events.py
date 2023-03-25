from utils import UserStates


def run(bot):
    @bot.callback_query_handler(func=lambda call: "suggest_" in call.data)
    async def suggest_query_handler(call):
        if call.data == str(UserStates.suggest_source):
            await bot.answer_callback_query(
                call.id,
                "Отправьте ссылку на источник"
            )
            await bot.send_message(
                call.message.chat.id,
                "Отправьте ссылку на источник с мероприятиями:"
            )
            await bot.set_state(call.from_user.id, UserStates.suggest_source, call.message.chat.id)
        if call.data == str(UserStates.suggest_functionality):
            await bot.answer_callback_query(
                call.id,
                "Предложите функционал"
            )
            await bot.send_message(
                call.message.chat.id,
                "Какие функции хотелось бы видеть в будущем?"
            )
            await bot.set_state(call.from_user.id, UserStates.suggest_functionality, call.message.chat.id)
