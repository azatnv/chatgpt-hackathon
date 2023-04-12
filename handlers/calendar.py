import os
import tempfile

from keyboard_buttons import menu_keyboard
from dao import get_actual_events, get_user_selected_comm, get_user_push_tags, get_actual_events_by_topic_list, \
    log_action
from icalendar import Calendar, Event, vText
from utils import filter_events_by_comm


def run(bot):
    async def add_to_calendar(events, message):
        event_list_add = list()
        for event in events:
            post_url = event[0]
            event_title = event[1]
            event_date = event[2]
            event_place = event[3] if event[3] else ""
            event_short_desc = event[4]
            comm_name = event[6]
            event_list_add.append([event_title, event_date, event_place,
                                   comm_name + "\n\n" + event_short_desc + "\n\n" + post_url])

        cal = Calendar()
        cal.add("prodid", "-//Levart//levart_bot//")
        cal.add("version", "2.0")
        cal.add("name", "Мероприятия от levart")
        cal.add("timezone", "Europe/Moscow")
        for event in event_list_add:
            cal_event = Event()
            cal_event.add('summary', event[0])
            cal_event.add('dtstart', event[1])
            cal_event.add('location', vText(event[2]))
            cal_event.add('description', event[3])
            cal.add_component(cal_event)

        await bot.send_message(
            message.chat.id,
            "Загрузите файл ICS, чтобы добавить в календарь.\n"
            "Также можно добавить каждое мероприятие отдельно, нажав на ссылки в сообщении.",
            disable_web_page_preview=True,
            reply_markup=menu_keyboard
        )
        directory = tempfile.mkdtemp()
        f = open(os.path.join(directory, f'Мероприятия - {message.from_user.username}.ics'), 'wb+')
        f.write(cal.to_ical())
        f.close()
        with open(os.path.join(directory, f'Мероприятия - {message.from_user.username}.ics'), 'rb') as f:
            await bot.send_document(message.chat.id, f)
        f.close()

    @bot.message_handler(commands=["ics"])
    async def add_to_calendar_all(message):
        await bot.delete_message(message.chat.id, message.message_id)

        log_action("add_to_calendar", message.from_user.id, message.from_user.username)

        user_tags = get_user_push_tags(message.from_user.id)
        if len(user_tags) == 0:
            user_tags = [1, 2, 3, 4, 5, 6]
        events = get_actual_events_by_topic_list(user_tags)
        user_communities = get_user_selected_comm(message.from_user.id)
        events = filter_events_by_comm(events, user_communities)

        if len(events) == 0:
            await bot.send_message(
                message.chat.id,
                "По указанным настройкам мероприятия не найдены!",
                reply_markup=menu_keyboard
            )
        else:
            await add_to_calendar(events, message)
