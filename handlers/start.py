import re

from dao import log_action, get_user_push_tags, set_user_push_tags, set_push_interval, check_new_user
from keyboard_buttons import menu_keyboard
from utils import UserStates, tag_id2text
from telebot import types


def run(bot):
    @bot.message_handler(commands=["start"])
    async def start_bot(message):
        check_new_user(message.from_user.id, message.from_user.username)

        log_action("start", message.from_user.id, message.from_user.username)

        await bot.set_state(message.from_user.id, UserStates.default, message.chat.id)
        await bot.delete_message(message.chat.id, message.message_id)

        tags_select_buttons = list()
        user_tags = get_user_push_tags(message.from_user.id)

        if len(user_tags) == 0:
            for tag_id in tag_id2text:
                tags_select_buttons.append(types.InlineKeyboardButton(f"✅ {tag_id2text[tag_id]}",
                                                                      callback_data=f"notifications_topic_{tag_id}"))
        else:
            for tag_id in tag_id2text:
                if tag_id in user_tags:
                    tags_select_buttons.append(types.InlineKeyboardButton(f"✅ {tag_id2text[tag_id]}",
                                                                          callback_data=f"notifications_topic_{tag_id}"))
                else:
                    tags_select_buttons.append(types.InlineKeyboardButton(tag_id2text[tag_id],
                                                                          callback_data=f"notifications_topic_{tag_id}"))
        notifications_topic_save_button = types.InlineKeyboardButton("Далее >",
                                                                     callback_data=f"start_save_notifications_topic")

        notifications_inline_keyboard = types.InlineKeyboardMarkup().add(*tags_select_buttons, row_width=2)
        notifications_inline_keyboard.add(notifications_topic_save_button)

        await bot.send_message(
            message.chat.id,
            "Выберите тематики, которые Вам интересны:",
            reply_markup=notifications_inline_keyboard
        )

    @bot.callback_query_handler(func=lambda call: "start_save_notifications_topic" == call.data)
    async def save_tags_select_query_handler(call):
        tags_select_keyboard = call.message.reply_markup.keyboard
        buttons_list = [button for sublist in tags_select_keyboard for button in sublist]
        selected_tags = list()
        for button in buttons_list:
            if "✅" in button.text:
                selected_tags.append(button.text.replace("✅ ", ""))
        if len(selected_tags) == 0:
            await bot.answer_callback_query(
                call.id,
                "Категории не выбраны",
                show_alert=True
            )
        else:
            tag_ids = list()
            for tag in selected_tags:
                key = list(filter(lambda x: tag_id2text[x] == tag, tag_id2text))[0]
                tag_ids.append(key)
            set_user_push_tags(call.from_user.id, tag_ids)
            await bot.answer_callback_query(call.id, "Категории сохранены")
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.send_message(
                call.message.chat.id,
                "Категории сохранены"
            )

            notifications_schedule_button_1 = types.InlineKeyboardButton("Ежедневно",
                                                                         callback_data="start_notifications_schedule_1")
            notifications_schedule_button_2 = types.InlineKeyboardButton("Каждые 3 дня",
                                                                         callback_data="start_notifications_schedule_2")
            notifications_schedule_button_3 = types.InlineKeyboardButton("Раз в неделю",
                                                                         callback_data="start_notifications_schedule_3")
            notifications_schedule_button_4 = types.InlineKeyboardButton("Раз в 2 недели",
                                                                         callback_data="start_notifications_schedule_4")
            notifications_schedule_button_5 = types.InlineKeyboardButton("Никогда",
                                                                         callback_data="start_notifications_schedule_5")

            notifications_inline_keyboard = types.InlineKeyboardMarkup().add(notifications_schedule_button_1,
                                                                             notifications_schedule_button_2,
                                                                             notifications_schedule_button_3,
                                                                             notifications_schedule_button_4,
                                                                             row_width=2)
            notifications_inline_keyboard.add(notifications_schedule_button_5)

            await bot.send_message(
                call.message.chat.id,
                "Выберите, как часто получать уведомления о мероприятиях:",
                reply_markup=notifications_inline_keyboard
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("start_notifications_schedule_"))
    async def notifications_schedule_select_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        call_data_search = re.search('notifications_schedule_(.+?)', call.data)
        n_button = int(call_data_search.group(1))

        if n_button == 1:
            set_push_interval(call.from_user.id, 1)
            await bot.send_message(
                call.message.chat.id,
                "Уведомления будут приходить ежедневно"
            )
        if n_button == 2:
            set_push_interval(call.from_user.id, 3)
            await bot.send_message(
                call.message.chat.id,
                "Уведомления будут приходить каждые 3 дня"
            )
        if n_button == 3:
            set_push_interval(call.from_user.id, 7)
            await bot.send_message(
                call.message.chat.id,
                "Уведомления будут приходить каждую неделю"
            )
        if n_button == 4:
            set_push_interval(call.from_user.id, 14)
            await bot.send_message(
                call.message.chat.id,
                "Уведомления будут приходить раз в 2 недели"
            )
        if n_button == 5:
            set_push_interval(call.from_user.id, 0)
            await bot.send_message(
                call.message.chat.id,
                "Уведомления отключены"
            )

        await bot.send_message(
            call.message.chat.id,
            """
Готово! ✅

С этого момента все мероприятия ИТМО с тобой в удобном формате.

Мероприятия по тематикам:
🗂 Все темы - /all
🧠 Образование - /edu
💵 Бизнес, инновации - /money
📈 Карьера - /career
💃 Развлечения - /fun
⚽️ Спорт - /sport
👀 Остальное - /other

Вывести в виде недели - /brief

Мы советуем добавлять мероприятия в календарь по ссылке, чтобы точно не забыть❗️

Добавить все мероприятия в календарь в формате .ICS - /ics
            """,
            reply_markup=menu_keyboard
        )
