#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pickle
from pathlib import Path


def _BackendRunner(fifo_path, func):
    """
    True background executors
    :param fifo_path: parameters with function, contain args and kwargs.
    :param func: Tasks that are executed in the background
    """
    with _ReadFifo(fifo_path) as rf:
        parameters = rf.parameters
        func(*parameters[0], **parameters[1])


class _ReadFifo:
    def __init__(self, fifo_path):
        self.__fifo_path = Path(fifo_path)
        self.__parameters = None

    def __enter__(self):
        with open(self.__fifo_path, "rb") as f:
            # noinspection PyBroadException
            try:
                self.__parameters = list(pickle.load(f))
            except BaseException as e:
                pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__fifo_path.exists():
            self.__fifo_path.unlink(missing_ok=True)

    @property
    def parameters(self):
        return self.__parameters


__all__ = [_BackendRunner]
