#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
class AsyncListener:
    """
    def task(params):
        params["a"] += 1

    def test_apply_async():
        chain = {"a": 1}
        listener = AsyncListener()
        ticker = Ticker(loops=3)
        ticker.apply_async(task, listener=listener, args=(chain,))
        listener.wait_task_status(10)
        assert chain['a'] == 4
    """
    def __init__(self):
        self.__status: bool = False

    def _set_task_status(self, status: bool):
        self.__status = status

    def get_task_status(self) -> bool:
        """
        Get async task run status. Requires the caller to actively poll for status
        """
        return self.__status

    def wait_task_status(self, timeout):
        """
        Proactively poll for task execution status, will block the process
        :param timeout: The polling timeout period, in seconds
        """
        start = datetime.datetime.now()
        while True:
            if (datetime.datetime.now() - start).seconds >= timeout or self.__status:
                break

from ._ticker import Ticker
from ._sched import Scheduler, SchedulerSync, SchedulerAsync, \
    SchedulerSyncProcess, SchedulerAsyncProcess, \
    SchedulerAsyncIO, SchedulerGevent

__all__ = [AsyncListener, Ticker, Scheduler, SchedulerSync, SchedulerAsync, SchedulerSyncProcess, SchedulerAsyncProcess,
           SchedulerAsyncIO, SchedulerGevent]