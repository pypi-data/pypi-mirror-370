#!/usr/bin/env python
# -*- coding:utf-8 -*-
import zoneinfo

from apscheduler.triggers.cron import CronTrigger, BaseField, MonthField, WeekField

from ..scheduler._cron._fields import DayOfMonthField, DayOfWeekField

__all__ = []


class CronTriggerExt(CronTrigger):
    """
    Triggers when current time matches all specified time constraints,
    similarly to how the UNIX cron scheduler works.

    :param str expr: cron expression

    Field       |   Required | Allowed values | Allow special characters  | Note
    Seconds	           Y	        0–59	            *,-
    Minutes	           Y	        0–59	            *,-
    Hours	           Y	        0–23	            *,-
    Day of month	   Y	        1–31	            *,-?
    Month	           Y	        1–12 or JAN–DEC	    *,-                  jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec
    Day of week	       Y	        0–6 or SUN–SAT	    *,-?                 mon,tue,wed,thu,fri,sat,sun
    Year	           N	        1970–2099	        *,-

    :param datetime.tzinfo|str timezone: time zone to use for the date/time calculations (defaults
        to scheduler timezone)
    :param int|None jitter: delay the job execution by ``jitter`` seconds at most
    """

    FIELDS_MAP = {
        'year': BaseField,
        'month': MonthField,
        'week': WeekField,
        'day': DayOfMonthField,
        'day_of_week': DayOfWeekField,
        'hour': BaseField,
        'minute': BaseField,
        'second': BaseField
    }

    def __init__(self, expr: str, timezone=None, jitter=None):
        cron = expr.split()
        if (cron_len := len(cron)) != 7:
            raise ValueError(f'Wrong number of fields; got {cron_len}, expected 7')
        super(CronTriggerExt, self).__init__(second=cron[0], minute=cron[1], hour=cron[2], day=cron[3], month=cron[4],
                                             day_of_week=cron[5], year=cron[6],
                                             timezone=timezone or zoneinfo.ZoneInfo("Asia/Shanghai"),
                                             jitter=jitter)
