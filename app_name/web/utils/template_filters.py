import datetime

from flask import url_for

THAI_MONTHS = [
    "มกราคม",
    "กุมภาพันธ์",
    "มีนาคม",
    "เมษายน",
    "พฤษภาคม",
    "มิถุนายน",
    "กรกฎาคม",
    "สิงหาคม",
    "กันยายน",
    "ตุลาคม",
    "พฤศจิกายน",
    "ธันวาคม",
]

THAI_SHORT_MONTHS = [
    "ม.ค.",
    "ก.พ.",
    "มี.ค.",
    "เม.ย.",
    "พ.ค.",
    "มิ.ย.",
    "ก.ค.",
    "ส.ค.",
    "ก.ย.",
    "ต.ค.",
    "พ.ย.",
    "ธ.ค.",
]


def static_url(filename: str):
    """url_for('static') with a daily cache-busting query string."""
    return add_date_url(url_for("static", filename=filename))


def add_date_url(url: str):
    now = datetime.datetime.now()
    return f"{url}?date={now.strftime('%Y%m%d')}"


def format_date(date: datetime.datetime, formatter: str = "%d/%m/%Y"):
    if not date:
        return "-"
    return date.strftime(formatter)


def format_number(data: str | int | float, digits: int = 0):
    return f"{float(data):,.{digits}f}"


def format_thai_date(dt: datetime.date, short_month: bool = False):
    if not isinstance(dt, datetime.date):
        return "-"

    months = THAI_SHORT_MONTHS if short_month else THAI_MONTHS
    return f"{dt.day} {months[dt.month - 1]} {dt.year + 543}"


def format_thai_datetime(dt: datetime.datetime, short_month: bool = True):
    if not isinstance(dt, datetime.datetime):
        return "-"

    return f"{format_thai_date(dt, short_month)} {dt.hour:02}:{dt.minute:02} น."


FILTERS = [
    static_url,
    add_date_url,
    format_date,
    format_number,
    format_thai_date,
    format_thai_datetime,
]
