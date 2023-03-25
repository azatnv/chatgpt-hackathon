import datetime
from urllib.parse import urlencode
from telebot.asyncio_handler_backends import StatesGroup, State

month_map = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря"
}

days_map = {
    0: "ПН",
    1: "ВТ",
    2: "СР",
    3: "ЧТ",
    4: "ПТ",
    5: "СБ",
    6: "ВС"
}


def get_date_string(date):
    now_day_number = date.weekday()
    short_str_day = days_map[now_day_number]
    month = month_map[date.month]
    day = date.day
    hour = date.hour
    minute = date.minute

    today = datetime.date.today()
    if today.day == date.day and \
            today.month == date.month and \
            today.year == date.year:
        if hour == 0:
            return f"Сегодня"
        else:
            return f"Сегодня в {hour:02d}:{minute:02d}"

    if (today + datetime.timedelta(1)).day == date.day and \
            (today + datetime.timedelta(1)).month == date.month and \
            (today + datetime.timedelta(1)).year == date.year:
        if hour == 0:
            return f"Завтра"
        else:
            return f"Завтра в {hour:02d}:{minute:02d}"

    if hour == 0:
        return f"{day} {month} ({short_str_day})"
    else:
        return f"{day} {month} ({short_str_day}) в {hour:02d}:{minute:02d}"


def make_google_cal_url(event_title, event_date, event_place, comm_name, event_short_desc, post_url):
    url = "https://www.google.com/calendar/render?action=TEMPLATE&"
    event_end_date = (event_date - datetime.timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ")
    event_date = (event_date - datetime.timedelta(hours=3)).strftime("%Y%m%dT%H%M%SZ")
    params = {"text": event_title, "details": comm_name + "\n\n" + event_short_desc + "\n\n" + post_url,
              "location": event_place, "dates": event_date + "/" + event_end_date}
    return url + urlencode(params)


def get_event_list_message_text(events, brief=False):
    event_list = []
    for i, event in enumerate(events, start=1):
        post_url = event[0]
        event_title = event[1]
        event_date = get_date_string(event[2])
        event_place = ""
        if event[3]:
            if "онлайн" in event[3].lower() or "online" in event[3].lower():
                event_place = f"📍 онлайн"
            else:
                event_place = f"📍 оффлайн"
        event_short_desc = event[4]
        comm_name = event[6]
        event_date_link = make_google_cal_url(event_title, event[2], event[3] if event[3] else "", comm_name,
                                              event_short_desc, post_url)
        if not brief:
            event_text = \
                f"\n\n🦄️ <a href='{post_url}'>{event_title}</a>" \
                f"\n🗓 {event_date} {event_place}" \
                f"\n{event_short_desc}"\
                f"\n<a href='{event_date_link}'>Добавить в календарь -></a>"
        else:
            event_text = f"\n\n🗓 {event_date} {event_place} - 🦄️ <a href='{post_url}'>{event_title}</a>"
        event_list.append(event_text)
    return event_list


class UserStates(StatesGroup):
    default = State()
    suggest_source = State()
    suggest_functionality = State()
    calendar_selection = State()
    add_to_calendar_all = State()
    add_to_calendar_week = State()
