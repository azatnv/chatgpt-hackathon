import re

from dao import log_action, all_groups, get_user_selected_comm, set_user_selected_comm, set_push_interval, \
    get_user_push_tags, set_user_push_tags
from telebot import types

from keyboard_buttons import menu_keyboard
from utils import tag_id2text


def run(bot):
    @bot.callback_query_handler(func=lambda call: "notifications_schedule" == call.data)
    async def notifications_schedule_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        log_action("notifications_schedule", call.from_user.id, call.from_user.username)

        notifications_schedule_button_1 = types.InlineKeyboardButton("Ежедневно",
                                                                     callback_data="notifications_schedule_1")
        notifications_schedule_button_2 = types.InlineKeyboardButton("Каждые 3 дня",
                                                                     callback_data="notifications_schedule_2")
        notifications_schedule_button_3 = types.InlineKeyboardButton("Раз в неделю",
                                                                     callback_data="notifications_schedule_3")
        notifications_schedule_button_4 = types.InlineKeyboardButton("Раз в 2 недели",
                                                                     callback_data="notifications_schedule_4")
        notifications_schedule_button_5 = types.InlineKeyboardButton("Никогда",
                                                                     callback_data="notifications_schedule_5")

        notifications_inline_keyboard = types.InlineKeyboardMarkup().add(notifications_schedule_button_1,
                                                                         notifications_schedule_button_2,
                                                                         notifications_schedule_button_3,
                                                                         notifications_schedule_button_4, row_width=2)
        notifications_inline_keyboard.add(notifications_schedule_button_5)

        await bot.send_message(
            call.message.chat.id,
            "Как часто мне присылать анонсы мероприятий:",
            reply_markup=notifications_inline_keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("notifications_schedule_"))
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
        notifications_schedule_button = types.InlineKeyboardButton("Уведомления 🔔",
                                                                   callback_data="notifications_schedule")
        notifications_topic_button = types.InlineKeyboardButton("Тематики 🗂",
                                                                callback_data="notifications_topic")
        settings_communities_button = types.InlineKeyboardButton("Источники мероприятий 📚",
                                                                 callback_data="settings_communities")
        commands_info_button = types.InlineKeyboardButton("Посмотреть команды бота ℹ️",
                                                          callback_data="commands_info")
        settings_cancel_button = types.InlineKeyboardButton("< В меню",
                                                            callback_data="settings_cancel")
        settings_inline_keyboard = types.InlineKeyboardMarkup().add(notifications_schedule_button,
                                                                    notifications_topic_button,
                                                                    settings_communities_button,
                                                                    commands_info_button,
                                                                    settings_cancel_button, row_width=1)
        await bot.send_message(
            call.message.chat.id,
            "Настройки:",
            reply_markup=settings_inline_keyboard
        )

    @bot.callback_query_handler(func=lambda call: "notifications_topic" == call.data)
    async def notifications_topic_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        log_action("notifications_topic", call.from_user.id, call.from_user.username)

        tags_select_buttons = list()
        user_tags = get_user_push_tags(call.from_user.id)

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
        notifications_topic_save_button = types.InlineKeyboardButton("💾 Сохранить 💾",
                                                                     callback_data=f"save_notifications_topic")

        notifications_inline_keyboard = types.InlineKeyboardMarkup().add(*tags_select_buttons, row_width=2)
        notifications_inline_keyboard.add(notifications_topic_save_button)

        await bot.send_message(
            call.message.chat.id,
            "Категории мероприятий, которые будут в уведомлениях:",
            reply_markup=notifications_inline_keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("notifications_topic_"))
    async def tags_select_query_handler(call):
        await bot.answer_callback_query(call.id)

        tags_select_keyboard = call.message.reply_markup.keyboard
        buttons_list = [button for sublist in tags_select_keyboard for button in sublist]
        for i, button in enumerate(buttons_list, start=0):
            if button.callback_data != call.data:
                continue
            else:
                if "✅" in button.text:
                    button.text = button.text.replace("✅ ", "")
                else:
                    button.text = "✅ " + button.text
                tags_select_keyboard[i // 2][i % 2] = button
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                            reply_markup=types.InlineKeyboardMarkup(tags_select_keyboard))

    @bot.callback_query_handler(func=lambda call: "save_notifications_topic" == call.data)
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
            notifications_schedule_button = types.InlineKeyboardButton("Уведомления 🔔",
                                                                       callback_data="notifications_schedule")
            notifications_topic_button = types.InlineKeyboardButton("Тематики 🗂",
                                                                    callback_data="notifications_topic")
            settings_communities_button = types.InlineKeyboardButton("Источники мероприятий 📚",
                                                                     callback_data="settings_communities")
            commands_info_button = types.InlineKeyboardButton("Посмотреть команды бота ℹ️",
                                                              callback_data="commands_info")
            settings_cancel_button = types.InlineKeyboardButton("< В меню",
                                                                callback_data="settings_cancel")
            settings_inline_keyboard = types.InlineKeyboardMarkup().add(notifications_schedule_button,
                                                                        notifications_topic_button,
                                                                        settings_communities_button,
                                                                        commands_info_button,
                                                                        settings_cancel_button, row_width=1)
            await bot.send_message(
                call.message.chat.id,
                "Настройки:",
                reply_markup=settings_inline_keyboard
            )

    @bot.callback_query_handler(func=lambda call: "settings_communities" == call.data)
    async def settings_communities_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        log_action("settings_communities", call.from_user.id, call.from_user.username)

        comm_select_buttons = list()
        user_communities = get_user_selected_comm(call.from_user.id)
        communities = all_groups
        if len(user_communities) == 0:
            for i, comm in enumerate(communities, start=0):
                comm_select_button = types.InlineKeyboardButton(f"✅ {comm[0]}", callback_data=f"comm_select_button_{i}")
                comm_select_buttons.append(comm_select_button)
        else:
            for i, comm in enumerate(communities, start=0):
                if comm[0] in user_communities:
                    comm_select_button = types.InlineKeyboardButton(f"✅ {comm[0]}",
                                                                    callback_data=f"comm_select_button_{i}")
                else:
                    comm_select_button = types.InlineKeyboardButton(comm[0],
                                                                    callback_data=f"comm_select_button_{i}")
                comm_select_buttons.append(comm_select_button)

        comm_select_keyboard = types.InlineKeyboardMarkup().add(*comm_select_buttons, row_width=1)
        comm_select_save_button = types.InlineKeyboardButton("💾 Сохранить 💾", callback_data=f"save_comm_select")
        comm_select_keyboard.add(comm_select_save_button)

        await bot.send_message(
            call.message.chat.id,
            "Выберите источники, из которых будут представлены мероприятия:",
            reply_markup=comm_select_keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("comm_select_button_"))
    async def comm_select_query_handler(call):
        await bot.answer_callback_query(call.id)

        comm_select_keyboard = call.message.reply_markup.keyboard
        buttons_list = [button for sublist in comm_select_keyboard for button in sublist]
        for i, button in enumerate(buttons_list, start=0):
            if button.callback_data != call.data:
                continue
            else:
                if "✅" in button.text:
                    button.text = button.text.replace("✅ ", "")
                else:
                    button.text = "✅ " + button.text
                comm_select_keyboard[i][0] = button
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                            reply_markup=types.InlineKeyboardMarkup(comm_select_keyboard))

    @bot.callback_query_handler(func=lambda call: "save_comm_select" == call.data)
    async def save_comm_select_query_handler(call):
        comm_select_keyboard = call.message.reply_markup.keyboard
        buttons_list = [button for sublist in comm_select_keyboard for button in sublist]
        selected_communities = list()
        for button in buttons_list:
            if "✅" in button.text:
                selected_communities.append(button.text.replace("✅ ", ""))
        if len(selected_communities) == 0:
            await bot.answer_callback_query(
                call.id,
                "Источники не выбраны",
                show_alert=True
            )
        else:
            set_user_selected_comm(call.from_user.id, selected_communities)
            await bot.answer_callback_query(call.id, "Источники мероприятий сохранены")
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.send_message(
                call.message.chat.id,
                "Источники мероприятий сохранены"
            )
            notifications_schedule_button = types.InlineKeyboardButton("Уведомления 🔔",
                                                                       callback_data="notifications_schedule")
            notifications_topic_button = types.InlineKeyboardButton("Тематики 🗂",
                                                                    callback_data="notifications_topic")
            settings_communities_button = types.InlineKeyboardButton("Источники мероприятий 📚",
                                                                     callback_data="settings_communities")
            commands_info_button = types.InlineKeyboardButton("Посмотреть команды бота ℹ️",
                                                              callback_data="commands_info")
            settings_cancel_button = types.InlineKeyboardButton("< В меню",
                                                                callback_data="settings_cancel")
            settings_inline_keyboard = types.InlineKeyboardMarkup().add(notifications_schedule_button,
                                                                        notifications_topic_button,
                                                                        settings_communities_button,
                                                                        commands_info_button,
                                                                        settings_cancel_button, row_width=1)
            await bot.send_message(
                call.message.chat.id,
                "Настройки:",
                reply_markup=settings_inline_keyboard
            )

    @bot.callback_query_handler(func=lambda call: "commands_info" == call.data)
    async def commands_info_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        log_action("commands_info", call.from_user.id, call.from_user.username)

        notifications_schedule_button = types.InlineKeyboardButton("< Назад", callback_data="back_to_settings")
        back_to_settings_keyboard = types.InlineKeyboardMarkup().add(notifications_schedule_button)
        await bot.send_message(
            call.message.chat.id,
            """
Мероприятия по тематикам:
🗂 Все темы - /all
🧠 Образование - /edu
💵 Бизнес, инновации - /money
📈 Карьера - /career
💃 Развлечения - /fun
⚽️ Спорт - /sport
👀 Остальное - /other

Вывести в виде недели - /brief

Мы советуем добавлять мероприятия в календарь по ссылке, чтобы точно не забыть❗

Добавить все мероприятия в календарь в формате .ICS - /ics
            """,
            reply_markup=back_to_settings_keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data == "settings_cancel")
    async def settings_cancel_query_handler(call):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(
            call.message.chat.id,
            "Меню",
            reply_markup=menu_keyboard
        )
