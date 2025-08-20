#!/usr/bin/env python
# -*- coding:utf-8 -*-
from inspect import getfullargspec
from threading import Thread
from time import time, sleep
from typing import Union

from . import AsyncListener
from collections.abc import Callable

__all__ = []


class Ticker(object):
    """
    A simple timer.
    """

    def __init__(self, *, interval: int = 1, loops: int = -1, end_time: Union[int, float] = None,
                 duration: Union[int, float] = None):
        """
        A simple scheduled task trigger
        :param interval: The interval for the next execution, in seconds.
        :param loops: total run times, if both loops and end_time are specified, the system exits when either is met.
        :param end_time: task end time, if both loops and end_time are specified, the system exits when either is met.
        :param duration: task run duration time
        """
        if not issubclass(type_ := type(interval), int):
            raise TypeError(f"interval expect type int, got {type_.__name__}")
        if not issubclass(type_ := type(loops), int):
            raise TypeError(f"loops expect type int, got {type_.__name__}")
        if end_time is not None and not issubclass(type_ := type(end_time), (int, float)):
            raise TypeError(f"end_time expect type int or float, got {type_.__name__}")
        if duration is not None and not issubclass(type_ := type(duration), int):
            raise TypeError(f"duration expect type int, got {type_.__name__}")
        self.__start: float = time()
        self.__now: float = self.__start
        self.__interval: int = interval
        self.__current_loops: int = 1
        self.__loops: int = loops
        self.__end_time: Union[int, float, None] = end_time
        self.__duration: Union[int, float, None] = duration
        self.__current_duration: float = 0

    def apply_sync(self, task: Callable = None, args: tuple = None, kwargs: dict = None):
        """
        Synchronize execution tasks.
        The task should not be expected to have a return.
        :param task: task FUNCTION.
        :param args: run task need's args.
        :param kwargs: run task need's kwargs. if kwargs contain 'ticker' key, will assign a Ticker object to it.

        if kwargs contain 'ticker' key, will assign a Ticker object to it.
        usage:
            @ticker_apply_async(interval=2, duration=10)
            def demo(ticker: Ticker = None):
                print("a:", ticker.end_time, ticker.now)
            demo()
        """
        kwargs_ = self.__join_this(task, kwargs or {})
        if issubclass(type(task), Callable):
            return self.__actuator(task, None, args or (), kwargs_)
        else:
            return self.__actuator_no_call(None)

    def apply_async(self, task: Callable = None, listener: AsyncListener = None, args: tuple = None,
                    kwargs: dict = None):
        """
        Asynchronous execution of tasks.
        The task should not be expected to have a return.
        :param listener:
        :param task: task.
        :param args: task args.
        :param kwargs: task kwargs. if kwargs contain 'ticker' key, will assign a Ticker object to it.

        if kwargs contain 'ticker' key, will assign a Ticker object to it.
        usage:
            @ticker_apply_async(interval=2, duration=10)
            def demo(ticker: Ticker = None):
                print("a:", ticker.end_time, ticker.now)
            demo()
        """
        kwargs_ = self.__join_this(task, kwargs or {})
        if issubclass(type(task), Callable):
            ticker_thread = Thread(target=self.__actuator, args=(task, listener, args or (), kwargs_))
        else:
            ticker_thread = Thread(target=self.__actuator_no_call, args=(listener,))
        ticker_thread.start()

    def __actuator(self, task: Callable, listener: AsyncListener or None, args: tuple, kwargs: dict):
        sleep(self.__interval)
        if (self.__loops and 0 <= self.__loops < self.__current_loops) \
                or (self.__end_time and self.__now > self.__end_time) \
                or (self.__duration and 0 <= self.__duration < self.__current_duration):
            if listener:
                listener._set_task_status(True)
            return
        task(*args, **kwargs)
        self.__now = time()
        self.__current_loops += 1
        self.__current_duration += self.__now - self.__start
        self.__actuator(task, listener, args, kwargs)

    def __actuator_no_call(self, listener: AsyncListener or None, ):
        if (self.__loops and 0 <= self.__loops < self.__current_loops) \
                or (self.__end_time and self.__now > self.__end_time) \
                or (self.__duration and 0 <= self.__duration < self.__current_duration):
            if listener:
                listener._set_task_status(True)
            return
        sleep(self.__interval)
        self.__now = time()
        self.__current_loops += 1
        self.__current_duration += self.__now - self.__start
        self.__actuator_no_call(listener)

    def __join_this(self, func, params):
        spec = getfullargspec(func)
        key = Ticker.__name__.lower()
        if key in spec.args or key in spec.kwonlyargs:
            params[key] = self
        return params

    @property
    def start_time(self) -> float:
        """
        task start run time
        """
        return self.__start

    @property
    def loops(self) -> int:
        """
        The total number of runs.
        """
        return self.__loops

    @property
    def current_loops(self) -> int:
        """
        The current running loop number.
        """
        return self.__current_loops

    @property
    def duration(self) -> float:
        """
        The Expected task run duration time.
        """
        return self.__duration

    @property
    def current_duration(self) -> float:
        """
        The current running duration time.
        :return:
        """
        return self.__current_duration

    @property
    def end_time(self) -> int:
        """
        Get task run end time.
        """
        return self.__end_time

    @property
    def now(self) -> float:
        """
        Current time
        """
        return self.__now
