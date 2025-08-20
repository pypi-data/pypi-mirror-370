#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from pathlib import Path
from typing import Union

from . import _check_type
from ..singleton import SingletonMeta

_RESOURCES = "resources"


class __PropertyConfig(metaclass=SingletonMeta):
    """
    Property   source   config
    """
    def __init__(self):
        self.__resources_dir: Path = Path.cwd().joinpath(_RESOURCES)

    def __str__(self):
        name = self.__class__.__name__
        return f"{name[2:]}({', '.join([f'{k.split(name[1:])[1][2:]}={v}' for k, v in self.__dict__.items()])})"

    def __repr__(self):
        return self.__str__()

    @property
    def resources(self) -> Path:
        """
        get properties file dir.
        It's not that the directory where the python file you run is called the working directory,
        but that when you run the script on the command line, the command line displays the directory you are in.
        """
        return self.__resources_dir

    @resources.setter
    def resources(self, value: Union[Path, str, os.PathLike]):
        """
        set resources dir.
        """
        _check_type(value, Path, str, os.PathLike)
        self.__resources_dir = Path(value)


PropertyConfig = __PropertyConfig()

__all__ = [PropertyConfig]
