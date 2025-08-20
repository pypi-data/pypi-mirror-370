#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import platform
import sys
from datetime import datetime
from enum import Enum
from locale import getpreferredencoding

from .. import config
from ..config.log import LogConfig
from ..collections import Deque
from ..converter import StorageUnit
from ..utils.computer import Disk


def __build_system_banner_info() -> dict:
    disk = Disk(str(LogConfig.dir.drive))
    system_properties = {
        "Python Version": platform.python_version(),
        "Python Compiler": platform.python_compiler(),
        "System Encoding": sys.getdefaultencoding(),
        "Terminal Encoding": getpreferredencoding(False),
        "OS Version": platform.platform(),
        "CPU": platform.processor(),
        "Disk Free": f"{disk.get_free(StorageUnit.MB)} MB ({disk.get_free_percent()}%) ",
        "Date Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Weekend": f"{datetime.now().strftime('%A')}"
    }
    system_info = {"title": "System Configuration", "properties": system_properties}
    return system_info


def _get_modules(path):
    """
    Gets the names of all non-__init__ modules under the package name
    """
    modules = []
    files = os.listdir(path)

    for file in files:
        name, _ = os.path.splitext(file)
        modules.append(f".{name}")
    return modules


def __build_frame_banner_infos() -> list:
    """
    Contains system properties
    """
    def gen_frame_config_info(class_):
        frame_config_info = {"title": class_.__doc__.strip()}
        frame_config_properties = {}
        frame_config_info["properties"] = frame_config_properties
        for k, v in class_.__dict__.items():
            if isinstance(v, Enum):
                value = v.name
            else:
                value = v
            frame_config_properties[k.split("__").pop().title().replace("_", " ")] = value
        frame_config_infos_append(frame_config_info)

    frame_config_infos = []
    frame_config_infos_append = frame_config_infos.append
    frame_config_infos_append(__build_system_banner_info())
    import importlib
    Deque.of_item(_get_modules(config.__path__[0])).stream \
        .filter(lambda n: not n.endswith("__") and not n.endswith("show")) \
        .map(lambda x: importlib.import_module(x, package=config.__name__)) \
        .map(lambda x: x.__all__) \
        .flat() \
        .filter(lambda x: x.__class__.__name__.endswith("Config")).for_each(gen_frame_config_info)
    return frame_config_infos
