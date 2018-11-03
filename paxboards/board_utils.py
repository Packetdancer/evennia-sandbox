import pytz
from django.utils.timezone import get_default_timezone


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def localize_datetime(timestamp, tz=None):
    if tz is not None and isinstance(tz, basestring):
        tz = pytz.timezone(tz)

    if not tz:
        tz = get_default_timezone()

    localized = timestamp.astimezone(tz)

    return localized


def datetime_to_date(timestamp, tz=None):
    return localize_datetime(timestamp, tz=tz).strftime("%Y/%m/%d")


def datetime_to_time(timestamp, tz=None):
    return localize_datetime(timestamp, tz=tz).strftime("%H:%M")


def datetime_to_full(timestamp, tz=None):
    return localize_datetime(timestamp, tz=tz).strftime("%Y/%m/%d %H:%M")
