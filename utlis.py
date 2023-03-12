



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