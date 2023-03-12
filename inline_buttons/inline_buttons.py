from telebot import types

#callback для /start
start_button = types.KeyboardButton("start", callback_data="start")
keyboard_client = types.ReplyKeyboardMarkup
keyboard_client.add(start_button)