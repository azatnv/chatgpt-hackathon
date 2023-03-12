import datetime


def get_next_weekday(date, weekday):  # weekday: 0 = Monday, 1=Tuesday, 2=Wednesday...
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


def get_current_sunday():
    today = datetime.date.today()
    current_sunday = get_next_weekday(today, 0) - datetime.timedelta(1)
    return current_sunday


def get_next_monday():
    today = datetime.date.today()
    next_monday = get_next_weekday(today, 0)
    return next_monday


def get_next_sunday():
    today = datetime.date.today()
    next_sunday = get_next_weekday(today, 6)
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
    if hour == 0:
        return f"{day} {month}"
    else:
        return f"{day} {month} ({short_str_day}) {hour:02d}:{minute:02d}"