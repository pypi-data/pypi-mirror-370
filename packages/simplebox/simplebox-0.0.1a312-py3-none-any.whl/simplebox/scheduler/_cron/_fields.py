#!/usr/bin/env python
# -*- coding:utf-8 -*-
from calendar import monthrange

from apscheduler.triggers.cron import BaseField
from apscheduler.triggers.cron.expressions import WeekdayPositionExpression, LastDayOfMonthExpression, \
    WeekdayRangeExpression

from ...scheduler._cron._expressions import UnknownExpression

__all__ = []


class DayOfMonthField(BaseField):
    COMPILERS = BaseField.COMPILERS + [WeekdayPositionExpression, LastDayOfMonthExpression, UnknownExpression]

    def get_max(self, dateval):
        return monthrange(dateval.year, dateval.month)[1]


class DayOfWeekField(BaseField):
    REAL = False
    COMPILERS = BaseField.COMPILERS + [WeekdayRangeExpression, UnknownExpression]

    def get_value(self, dateval):
        return dateval.weekday()
