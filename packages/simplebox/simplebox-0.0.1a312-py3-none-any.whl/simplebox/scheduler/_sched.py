#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Callable

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.gevent import GeventExecutor
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from psutil import cpu_count

from ..scheduler._base import CronTriggerExt
from ..utils.objects import ObjectsUtils

__all__ = []


_THREAD_POOLS = 20
_PROCESS_POOLS = int(cpu_count() / 2) or 1


class Scheduler:

    def __init__(self, scheduler: BaseScheduler, trigger: CronTriggerExt, executors):
        ObjectsUtils.call_limit(__file__)
        self.__scheduler: BaseScheduler = scheduler
        self.__opts = {"trigger": trigger, "executors": {"default": executors}}

    def run(self, action: Callable, args: tuple = None, kwargs: dict = None):
        """
        Execute the scheduler
        :param action: task
        :param args: list of positional arguments to task with
        :param kwargs: dict of keyword arguments to task with
        """
        self.__scheduler.add_job(action, **self.__opts, args=args, kwargs=kwargs)
        self.__scheduler.start()


class SchedulerSync(Scheduler):
    """
    When the scheduler is the only thing in your app to run.
    Executor use thread pool.
    """

    def __init__(self, cron, pools: int = _THREAD_POOLS, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param pools: pool size
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        super().__init__(BlockingScheduler(), CronTriggerExt(cron, timezone=timezone, jitter=jitter),
                         ThreadPoolExecutor(pools))


class SchedulerAsync(Scheduler):
    """
    Used when you're not running any other framework and want the scheduler to execute in the background of your app
    (this is how charging stations use).
    Executor use thread pool.

    ex:

    def task(params):
        params["a"] += 1

    def test():
        chain = {"a": 1}
        scheduler = SchedulerAsync("*/3 * * * * ? *")
        scheduler.run(task, args=(chain, ))
        time.sleep(5)
        assert chain['a'] == 3
    """

    def __init__(self, cron, pools: int = _THREAD_POOLS, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param pools: pool size
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        super().__init__(BackgroundScheduler(), CronTriggerExt(cron, timezone=timezone, jitter=jitter),
                         ThreadPoolExecutor(pools))


class SchedulerSyncProcess(Scheduler):
    """
    When the scheduler is the only thing in your app to run.
    Executor use process pool.
    """

    def __init__(self, cron, pools: int = _PROCESS_POOLS, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param pools: pool size
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        super().__init__(BlockingScheduler(), CronTriggerExt(cron, timezone=timezone, jitter=jitter),
                         ProcessPoolExecutor(pools))


class SchedulerAsyncProcess(Scheduler):
    """
    Used when you're not running any other framework and want the scheduler to execute in the background of your app
    (this is how charging stations use).
    Executor use process pool.
    """

    def __init__(self, cron, pools: int = _PROCESS_POOLS, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param pools: pool size
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        super().__init__(BackgroundScheduler(), CronTriggerExt(cron, timezone=timezone, jitter=jitter),
                         ProcessPoolExecutor(pools))


class SchedulerAsyncIO(Scheduler):
    """
    Use when your program uses asyncio, an asynchronous framework.
    """

    def __init__(self, cron, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        super().__init__(AsyncIOScheduler(), CronTriggerExt(cron, timezone=timezone, jitter=jitter), AsyncIOExecutor())


class SchedulerGevent(Scheduler):
    """
    Use when your program uses gevent, the high-performance Python concurrency framework.
    """

    def __init__(self, cron, timezone=None, jitter=None):
        """
        :param cron: cron expression
        :param timezone: time zone to use for the date/time calculations (defaults Asia/Shanghai)
        :param jitter: delay the job execution by ``jitter`` seconds at most
        """
        super().__init__(GeventScheduler(), CronTriggerExt(cron, timezone=timezone, jitter=jitter), GeventExecutor())
