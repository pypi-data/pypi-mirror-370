#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import Union, Optional

from ..singleton import SingletonMeta
from .log import LogLevel

B = Union[bool, str]


class __RestConfig(metaclass=SingletonMeta):
    """
    Rest global configuration
    """

    def __init__(self):
        self.__allow_redirection: bool = True
        self.__check_status: bool = False
        self.__encoding: str = "utf-8"
        self.__http_log_level: LogLevel = LogLevel.DEBUG

    def __str__(self):
        name = self.__class__.__name__
        return f"{name[2:]}({', '.join([f'{k.split(name[1:])[1][2:]}={v}' for k, v in self.__dict__.items()])})"

    def __repr__(self):
        return self.__str__()

    @property
    def allow_redirection(self) -> bool:
        return self.__allow_redirection

    @allow_redirection.setter
    def allow_redirection(self, value: B):
        self.__set_allow_redirection(value)

    def __set_allow_redirection(self, value: B):
        if issubclass(v_type := (type(value)), bool):
            self.__allow_redirection = value
        elif issubclass(v_type, str):
            self.__allow_redirection = _to_bool(value, True)

    @property
    def check_status(self) -> bool:
        return self.__check_status

    @check_status.setter
    def check_status(self, value: B):
        self.__set_check_status(value)

    def __set_check_status(self, value: B):
        if issubclass(v_type := (type(value)), bool):
            self.__check_status = value
        elif issubclass(v_type, str):
            self.__check_status = _to_bool(value, False)

    @property
    def encoding(self) -> str:
        return self.__encoding

    @encoding.setter
    def encoding(self, value: Optional[str]):
        self.__set_encoding(value)

    def __set_encoding(self, value: Optional[str]):
        if issubclass(type(value), str):
            self.__encoding = value

    @property
    def http_log_level(self) -> LogLevel:
        """
        only set http request and response info's log level.
        """
        return self.__http_log_level

    @http_log_level.setter
    def http_log_level(self, level: LogLevel or int or str):
        if isinstance(level, LogLevel):
            self.__http_log_level = level
        elif isinstance(level, str):
            self.__http_log_level = LogLevel.get_by_name(level, self.__http_log_level)
        elif isinstance(level, int):
            self.__http_log_level = LogLevel.get_by_value(level, self.__http_log_level)


def _to_bool(value: str, default: bool = False) -> bool:
    """
    Converts the string bool type to a true bool type.
    :param value: string bool type.
    :param default: If it is not of type string bool, the value returned by default.
    """
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        if value == "True" or value == "true":
            return True
        elif value == "False" or value == "false":
            return False
    return default


RestConfig: __RestConfig = __RestConfig()

__all__ = [RestConfig]
