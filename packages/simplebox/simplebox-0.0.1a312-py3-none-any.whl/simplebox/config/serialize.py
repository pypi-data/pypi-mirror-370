#!/usr/bin/env python
# -*- coding:utf-8 -*-
from . import _check_type
from ..singleton import SingletonMeta


class __SerializeConfig(metaclass=SingletonMeta):
    """
    Serializable module global config
    """

    def __init__(self):
        self.__autoname: bool = False
        self.__camel: bool = False

    def __str__(self):
        name = self.__class__.__name__
        return f"{name[2:]}({', '.join([f'{k.split(name[1:])[1][2:]}={v}' for k, v in self.__dict__.items()])})"

    def __repr__(self):
        return self.__str__()

    @property
    def autoname(self) -> bool:
        """
        If the name of the json field is not specified and the autoname is True,
        the python attribute name will be tried as the json field name, and the private attribute
        will try to be replaced with a public attribute (only if serialized).
        :return:
        """
        return self.__autoname

    @autoname.setter
    def autoname(self, value: bool):
        _check_type(value, bool)
        self.__autoname = value

    @property
    def camel(self) -> bool:
        """
        The recommended attribute format for python is snake, and this option will use camel.
        :return:
        """
        return self.__camel

    @camel.setter
    def camel(self, value: bool):
        _check_type(value, bool)
        self.__camel = value


SerializeConfig = __SerializeConfig()

__all__ = [SerializeConfig]
