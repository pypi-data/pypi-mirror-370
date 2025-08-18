import datetime as dt
import time
from dateutil import parser as dt_parser


def now():
    return dt.datetime.fromtimestamp(time.time(), dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def string_to_datetime(datetime_str):
    return dt_parser.parse(
        datetime_str
        or dt.datetime.fromtimestamp(0, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
