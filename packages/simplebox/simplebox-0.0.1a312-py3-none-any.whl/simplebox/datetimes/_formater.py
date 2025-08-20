#!/usr/bin/env python
# -*- coding:utf-8 -*-
from datetime import datetime
from enum import Enum


class Datetime:
    def __init__(self, formatter: str):
        self.__formatter: str = formatter

    def format(self, dt: datetime or float, tz=None) -> str:
        if isinstance(dt, datetime):
            return dt.strftime(self.__formatter)
        elif isinstance(dt, float):
            return datetime.fromtimestamp(dt, tz).strftime(self.__formatter)
        raise TypeError(f'not support type: {type(dt).__name__}')

    def parser(self, datetime_string: str, to_timestamp: bool = False) -> datetime or float:
        dt = datetime.strptime(datetime_string, self.__formatter)
        if to_timestamp:
            return dt.timestamp()
        return dt


class DatetimeFormatter(Enum):
    DEFAULT = Datetime("%Y-%m-%d %H:%M:%S")
    YEAR_MONTH_DAY = Datetime("%Y-%m-%d")
    HOUR_MIN_SEC = Datetime("%H:%M:%S")
    YEAR_MONTH_DAY_START = Datetime("%Y-%m-%d 00:00:00")
    YEAR_MONTH_DAY_END = Datetime("%Y-%m-%d 23:59:59")

    def format(self, dt: datetime or float, tz=None):
        """
        Convert a date time object or timestamp to a string.
        :param dt: datetime or timestamp
        :param tz: time zone.
        :return:
        """
        self.value.format(dt, tz)

    def parser(self, datetime_string: str, to_timestamp: bool = False):
        """
        Convert the date and time of the string to a different timestamp or timestamp.
        :param to_timestamp: return timestamp.
        :param datetime_string: string format datetime.
        :return:
        """
        return self.value.parser(datetime_string)