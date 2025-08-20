#!/usr/bin/env python
# -*- coding:utf-8 -*-
from enum import Enum
from typing import TypeVar, Union, Iterable

from .generic import T
from .utils.enums import EnumUtils

_ET = TypeVar("_ET", bound=Union[Enum])


class EnhanceEnum(Enum):
    """
    Enumerates enhanced classes that provide some tool methods.
    """

    @classmethod
    def has_value(cls, value: T) -> bool:
        """
        Determines whether the enumeration contains members of the specified value
        """
        return EnumUtils.has_value(cls, value)

    @classmethod
    def has_name(cls, name: str) -> bool:
        """
        Determines whether the enumeration contains members with the specified name
        """
        return EnumUtils.has_name(cls, name)

    @classmethod
    def get_by_name(cls, name: str, default: _ET = None) -> _ET:
        """
        Gets the enumeration object by the enumeration name
        :param name: Enumerates element name
        :param default: If the default value is not found
        """
        return EnumUtils.get_by_name(cls, name, default)

    @classmethod
    def get_by_value(cls, value: T, default: _ET = None) -> _ET:
        """
        Gets the enumeration object from the enumeration value
        :param value: Enumerates element value
        :param default: If the default value is not found
        """
        return EnumUtils.get_by_value(cls, value, default)

    @classmethod
    def to_dict(cls) -> dict[str, T]:
        """
        Convert the enumeration to a dictionary
        """
        return EnumUtils.to_dict(cls)

    @classmethod
    def get_keys(cls) -> Iterable:
        """
        get all key in enum.
        :return:
        """
        return (k for k in EnumUtils.to_dict(cls).keys())

    @classmethod
    def get_values(cls) -> Iterable:
        """
        get all value in enum.
        :return:
        """
        return (k for k in EnumUtils.to_dict(cls).values())


__all__ = [EnhanceEnum]
