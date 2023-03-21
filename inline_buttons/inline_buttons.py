from telebot import types

menu_button = types.KeyboardButton("Меню")

# все мероприятия
events_button = types.KeyboardButton("Мероприятия")
# источники
event_sources_button = types.KeyboardButton("Источники мероприятий")
# предложить как улучшить бота
suggest_improvement_button = types.KeyboardButton("Предложить улучшение")


menu_keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
)
menu_keyboard.\
    add(events_button).\
    add(event_sources_button, suggest_improvement_button)

init_keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
)
init_keyboard.add(events_button).add(menu_button)
