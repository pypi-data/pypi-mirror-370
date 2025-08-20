#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Callable
from typing import Optional, Any

from . import _check_type
from ..singleton import SingletonMeta


class __JsonConfig(metaclass=SingletonMeta):
    """
    simplebox.json global config.
    use in simplebox.json module.
    """

    def __init__(self):
        self.__newline: bool = False
        self.__indent2: bool = False
        self.__naive_utc: bool = False
        self.__non_str_keys: bool = False
        self.__omit_microseconds: bool = False
        self.__passthrough_dataclass: bool = False
        self.__passthrough_datetime: bool = False
        self.__passthrough_subclass: bool = False
        self.__serialize_dataclass: bool = False
        self.__serialize_numpy: bool = False
        self.__serialize_uuid: bool = False
        self.__sort_keys: bool = False
        self.__strict_integer: bool = False
        self.__utc_z: bool = False
        self.__default: Optional[Callable[[Any], Any]] = None

    def __str__(self):
        name = self.__class__.__name__
        return f"{name[2:]}({', '.join([f'{k.split(name[1:])[1][2:]}={v}' for k, v in self.__dict__.items()])})"

    def __repr__(self):
        return self.__str__()

    @property
    def newline(self) -> bool:
        return self.__newline

    @newline.setter
    def newline(self, value):
        _check_type(value, bool)
        self.__newline = value

    @property
    def indent2(self) -> bool:
        return self.__indent2

    @indent2.setter
    def indent2(self, value):
        _check_type(value, bool)
        self.__indent2 = value

    @property
    def naive_utc(self) -> bool:
        return self.__naive_utc

    @naive_utc.setter
    def naive_utc(self, value):
        _check_type(value, bool)
        self.__naive_utc = value

    @property
    def non_str_keys(self) -> bool:
        return self.__non_str_keys

    @non_str_keys.setter
    def non_str_keys(self, value: bool):
        _check_type(value, bool)
        self.__non_str_keys = value

    @property
    def omit_microseconds(self) -> bool:
        return self.__omit_microseconds

    @omit_microseconds.setter
    def omit_microseconds(self, value: bool):
        _check_type(value, bool)
        self.__omit_microseconds = value

    @property
    def passthrough_dataclass(self) -> bool:
        return self.__passthrough_dataclass

    @passthrough_dataclass.setter
    def passthrough_dataclass(self, value: bool):
        _check_type(value, bool)
        self.__passthrough_dataclass = value

    @property
    def passthrough_datetime(self) -> bool:
        return self.__passthrough_datetime

    @passthrough_datetime.setter
    def passthrough_datetime(self, value: bool):
        _check_type(value, bool)
        self.__passthrough_datetime = value

    @property
    def passthrough_subclass(self) -> bool:
        return self.__passthrough_subclass

    @passthrough_subclass.setter
    def passthrough_subclass(self, value: bool):
        _check_type(value, bool)
        self.__passthrough_subclass = value

    @property
    def serialize_dataclass(self) -> bool:
        return self.__serialize_dataclass

    @serialize_dataclass.setter
    def serialize_dataclass(self, value: bool):
        _check_type(value, bool)
        self.__serialize_dataclass = value

    @property
    def serialize_numpy(self) -> bool:
        return self.__serialize_numpy

    @serialize_numpy.setter
    def serialize_numpy(self, value: bool):
        _check_type(value, bool)
        self.__serialize_numpy = value

    @property
    def serialize_uuid(self) -> bool:
        return self.__serialize_uuid

    @serialize_uuid.setter
    def serialize_uuid(self, value: bool):
        _check_type(value, bool)
        self.__serialize_uuid = value

    @property
    def sort_keys(self) -> bool:
        return self.__sort_keys

    @sort_keys.setter
    def sort_keys(self, value: bool):
        _check_type(value, bool)
        self.__sort_keys = value

    @property
    def strict_integer(self) -> bool:
        return self.__strict_integer

    @strict_integer.setter
    def strict_integer(self, value: bool):
        _check_type(value, bool)
        self.__strict_integer = value

    @property
    def utc_z(self) -> bool:
        return self.__utc_z

    @utc_z.setter
    def utc_z(self, value: bool):
        _check_type(value, bool)
        self.__utc_z = value

    @property
    def default(self) -> Optional[Callable[[Any], Any]]:
        return self.__default

    @default.setter
    def default(self, value: Optional[Callable[[Any], Any]]):
        _check_type(value, Callable)
        self.__default = value


JsonConfig = __JsonConfig()

__all__ = [JsonConfig]
