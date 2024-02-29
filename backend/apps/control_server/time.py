from datetime import datetime

from pytz import utc


def now():
    """
    Returns current time in UTC.
    :return:
    """
    return datetime.utcnow().replace(tzinfo=utc)


def now_string():
    """
    Returns the current server time as a string.
    :return:
    """
    return now().strftime("%Y-%m-%d %H:%M:%S")
