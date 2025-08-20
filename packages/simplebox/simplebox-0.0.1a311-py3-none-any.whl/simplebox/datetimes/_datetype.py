#!/usr/bin/env python
# -*- coding:utf-8 -*-
from datetime import time, datetime, date, timedelta
from typing import Union

from ..datetimes import DatetimeFormatter

__all__ = []

from ..exceptions import DateTimeParseValueErrorException, DateTimeParseTypeErrorException

TimeType = Union[tuple[int, int, int], list[int, int, int], time, datetime]
DateType = Union[tuple[int, int, int], list[int, int, int], date, datetime]
DateTimeType = Union[tuple[int, int, int, int, int, int], list[int, int, int, int, int, int], str, datetime]
NumberType = Union[int, float]
DiffType = [timedelta, int, float]


def _handle_time_type(origin) -> time:
    if isinstance(origin, time):
        return origin
    elif isinstance(origin, datetime):
        return origin.time()
    elif isinstance(origin, (tuple, list)):
        if len(origin) != 3:
            raise DateTimeParseValueErrorException(f"TimeType tuple format need 3 values. like: (23, 59, 59)")
        return time(origin[0], origin[1], origin[2])
    else:
        raise DateTimeParseTypeErrorException(f"not support type '{type(origin).__name__}'")


def _handle_date_type(origin) -> date:
    if isinstance(origin, datetime):
        return origin.date()
    elif isinstance(origin, date):
        return origin
    elif isinstance(origin, (tuple, list)):
        if len(origin) != 3:
            raise DateTimeParseValueErrorException(f"DateType tuple format need 3 values. like: (1970, 1, 1)")
        return date(origin[0], origin[1], origin[2])
    else:
        raise DateTimeParseTypeErrorException(f"not support type '{type(origin).__name__}'")


def _handle_datetime_type(origin, str_format: Union[str, DatetimeFormatter] = None) -> datetime:
    if isinstance(origin, datetime):
        return origin
    elif isinstance(origin, (tuple, list)):
        if length := len(origin) == 6:
            return datetime(origin[0], origin[1], origin[2], origin[3], origin[4], origin[5])
        elif length == 3:
            return datetime.combine(date(origin[0], origin[1], origin[2]), time.min)
        else:
            raise DateTimeParseValueErrorException(f"DateTimeType tuple format need 6 or 3 values. "
                                                   f"like: (1970, 1, 1, 23, 59, 59) or (1970, 1, 1)")
    elif isinstance(origin, (int, float)):
        return datetime.fromtimestamp(origin)
    elif isinstance(origin, str):
        if isinstance(str_format, str):
            return datetime.strptime(origin, str_format)
        elif isinstance(str_format, DatetimeFormatter):
            return str_format.parser(origin)
        else:
            return DatetimeFormatter.DEFAULT.parser(origin)
    else:
        raise DateTimeParseTypeErrorException(f"not support type '{type(origin).__name__}'")


def _handle_diff_type(origin) -> float:
    if isinstance(origin, timedelta):
        return origin.days
    elif isinstance(origin, (int, float)):
        return origin
    else:
        raise DateTimeParseTypeErrorException(
            f"expected type 'timedelta or int or float', got a {type(origin).__name__}")
