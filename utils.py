import datetime


def get_next_weekday(date, weekday):  # weekday: 0 = Monday, 1=Tuesday, 2=Wednesday...
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


def get_current_sunday():
    today = datetime.date.today()
    next_monday = get_next_weekday(today, 0)
    next_monday.day -= 1
    next_monday.hour = 23
    next_monday.minute = 59
    current_sunday = next_monday
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

def get_date_string(date):
    month = month_map[date.month]
    day = date.day
    hour = date.hour
    minute = date.minute
    if hour == 0:
        return f"{day} {month}"
    else:
        return f"{day} {month} {hour:02d}:{minute:02d}"