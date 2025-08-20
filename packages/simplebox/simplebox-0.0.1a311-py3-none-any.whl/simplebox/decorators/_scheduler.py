#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Callable
from functools import wraps

from psutil import cpu_count

from ..generic import T
from ..scheduler import SchedulerSync, SchedulerAsync, SchedulerSyncProcess, SchedulerAsyncProcess, SchedulerAsyncIO, \
    SchedulerGevent

_THREAD_POOLS = 20
_PROCESS_POOLS = int(cpu_count() / 2) or 1


def scheduler_sync(cron, pools: int = _THREAD_POOLS, timezone=None, jitter=None) -> T:
    """
    SchedulerSync's decorator mode, reference SchedulerSync.
    """

    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return __do_scheduler_sync(func, args, kwargs, cron, pools, timezone, jitter)

        return __wrapper

    return __inner


def scheduler_async(cron, pools: int = _THREAD_POOLS, timezone=None, jitter=None) -> T:
    """
    SchedulerAsync's decorator mode, reference SchedulerAsync.
    """

    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return __do_scheduler_async(func, args, kwargs, cron, pools, timezone, jitter)

        return __wrapper

    return __inner


def scheduler_sync_process(cron, pools: int = _THREAD_POOLS, timezone=None, jitter=None) -> T:
    """
    SchedulerSyncProcess's decorator mode, reference SchedulerSyncProcess.
    """

    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return __do_scheduler_sync_process(func, args, kwargs, cron, pools, timezone, jitter)

        return __wrapper

    return __inner


def scheduler_async_process(cron, pools: int = _THREAD_POOLS, timezone=None, jitter=None) -> T:
    """
    SchedulerAsyncProcess's decorator mode, reference SchedulerAsyncProcess.
    """

    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return __do_scheduler_async_process(func, args, kwargs, cron, pools, timezone, jitter)

        return __wrapper

    return __inner


def scheduler_asyncio(cron, timezone=None, jitter=None) -> T:
    """
    SchedulerAsyncIO's decorator mode, reference SchedulerAsyncIO.
    """

    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return __do_scheduler_asyncio(func, args, kwargs, cron, timezone, jitter)

        return __wrapper

    return __inner


def scheduler_gevent(cron, timezone=None, jitter=None) -> T:
    """
    SchedulerGevent's decorator mode, reference SchedulerGevent.
    """

    def __inner(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            return __do_scheduler_gevent(func, args, kwargs, cron, timezone, jitter)

        return __wrapper

    return __inner


def __do_scheduler_sync(func: Callable, args: tuple = None, kwargs: dict = None, cron=None,
                        pools: int = _THREAD_POOLS, timezone=None, jitter=None):
    SchedulerSync(cron, pools, timezone, jitter).run(func, args, kwargs)


def __do_scheduler_async(func: Callable, args: tuple = None, kwargs: dict = None, cron=None,
                         pools: int = _THREAD_POOLS, timezone=None, jitter=None):
    SchedulerAsync(cron, pools, timezone, jitter).run(func, args, kwargs)


def __do_scheduler_sync_process(func: Callable, args: tuple = None, kwargs: dict = None, cron=None,
                                pools: int = _THREAD_POOLS, timezone=None, jitter=None):
    SchedulerSyncProcess(cron, pools, timezone, jitter).run(func, args, kwargs)


def __do_scheduler_async_process(func: Callable, args: tuple = None, kwargs: dict = None, cron=None,
                                 pools: int = _THREAD_POOLS, timezone=None, jitter=None):
    SchedulerAsyncProcess(cron, pools, timezone, jitter).run(func, args, kwargs)


def __do_scheduler_asyncio(func: Callable, args: tuple = None, kwargs: dict = None, cron=None,
                           timezone=None, jitter=None):
    SchedulerAsyncIO(cron, timezone, jitter).run(func, args, kwargs)


def __do_scheduler_gevent(func: Callable, args: tuple = None, kwargs: dict = None, cron=None,
                          timezone=None, jitter=None):
    SchedulerGevent(cron, timezone, jitter).run(func, args, kwargs)


__all__ = []
