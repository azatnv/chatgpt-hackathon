from telebot import types

events_button = types.KeyboardButton("Мероприятия 👀")
settings_button = types.KeyboardButton("Настройки ⚙️")

menu_keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
)
menu_keyboard.add(events_button).add(settings_button)
