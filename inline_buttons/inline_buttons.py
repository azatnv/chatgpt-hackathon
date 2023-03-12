from telebot import types

start_button = types.KeyboardButton("Ближайшие мероприятия")
init_keyboard_client = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
)
init_keyboard_client.add(start_button)


event_sources_button = types.KeyboardButton("Источники мероприятий")
keyboard_client = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
)
keyboard_client.add(event_sources_button)

