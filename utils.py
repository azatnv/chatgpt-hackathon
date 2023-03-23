import datetime
from urllib.parse import urlencode

from telebot.asyncio_handler_backends import StatesGroup, State


def get_next_weekday(date, weekday):  # weekday: 0 = Monday, 1=Tuesday, 2=Wednesday...
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


def get_next_monday():
    today = datetime.date.today()
    next_monday = get_next_weekday(today, 0)
    return next_monday


def get_current_sunday():
    next_monday = get_next_monday()
    current_sunday = next_monday - datetime.timedelta(1)
    return current_sunday


def get_next_sunday():
    next_monday = get_next_monday()  # next monday
    next_sunday = get_next_weekday(next_monday, 6)
    return next_sunday


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


def make_google_cal_url(event_title, event_date, event_place, comm_name, event_short_desc):
    url = "https://www.google.com/calendar/render?action=TEMPLATE&"
    event_end_date = (event_date - datetime.timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ")
    event_date = (event_date - datetime.timedelta(hours=3)).strftime("%Y%m%dT%H%M%SZ")
    params = {"text": event_title, "details": comm_name + "\n" + event_short_desc, "location": event_place, "dates": event_date + "/" + event_end_date}
    return url + urlencode(params)


class UserStates(StatesGroup):
    default = State()
    suggest_source = State()
    suggest_functionality = State()
    calendar_selection = State()
    add_to_calendar = State()
