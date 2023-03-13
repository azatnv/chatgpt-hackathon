from telebot import types

menu_button = types.KeyboardButton("Меню")

# ближайшие
nearest_tree_event_button = types.KeyboardButton("Ближайшие мероприятия")
# источники
event_sources_button = types.KeyboardButton("Источники мероприятий")
# на этой неделе:
current_week_button = types.KeyboardButton("Текущая неделя")
# на следующей:
next_week_button = types.KeyboardButton("Следующая неделя")


menu_keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
)
menu_keyboard.\
    row(nearest_tree_event_button, next_week_button).\
    add(event_sources_button)
    # row(current_week_button).add(next_week_button)

init_keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
)
init_keyboard.add(nearest_tree_event_button).add(menu_button)

link_to_menu_keyboard = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
)
link_to_menu_keyboard.add(menu_button)



