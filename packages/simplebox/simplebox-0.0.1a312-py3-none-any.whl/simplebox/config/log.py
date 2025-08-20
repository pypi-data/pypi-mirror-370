#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
from pathlib import Path
from time import strftime
from typing import Optional, Union

from . import _check_type
from ..converter import StorageUnit
from ..enums import EnhanceEnum
from ..singleton import SingletonMeta
from ..utils.strings import StringUtils


class LogLevel(EnhanceEnum):
    """
    log level
    ignore
    """
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOSET = 0


L = Union[LogLevel, str, int]
B = Union[bool, str]


class __LogConfig(metaclass=SingletonMeta):
    """
    Log global configuration
    """

    def __init__(self):
        self.__dir: Optional[Path] = None
        self.__level: LogLevel = LogLevel.NOSET
        self.__level_console = LogLevel.NOSET
        self.__level_file = LogLevel.NOSET
        self.__format: str = f"[%(asctime)s {strftime('%z')}]-[%(process)s]-[%(thread)s]-[%(traceid)s]-[%(filename)s]" \
                             f"-[lineno:%(lineno)s]-[%(name)s]-[%(levelname)s] %(message)s"
        self.__coding: str = "utf-8"
        self.__name: str = f"simplebox-{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}.log"
        self.__rotating_when: str = "midnight"
        self.__max_bytes: int = StorageUnit.MB.of(100).to(StorageUnit.BYTE).integer()
        self.__delay: bool = False
        self.__cut_mode: int = 1
        self.__backup_count: int = 30
        self.__off_banner: bool = False
        self.__off_file: bool = True
        self.__off_console: bool = False
        self.__off: bool = False
        self.__path: Optional[Path] = None
        self.__set_dir(Path.cwd().absolute())
        self.__set_path(self.dir, self.__name)

    def __str__(self):
        name = self.__class__.__name__
        return f"{name[2:]}({', '.join([f'{k.split(name[1:])[1][2:]}={v}' for k, v in self.__dict__.items()])})"

    def __repr__(self):
        return self.__str__()

    @property
    def dir(self) -> Optional[Path]:
        return self.__dir

    @dir.setter
    def dir(self, value: Union[Path, str]):
        """
        value will append 'logs' folder.
        default path in command work dir.
        Example:
            LogConfig.dir = /tmp/
            print(LogConfig.dir) = /tmp/logs/
        """
        _check_type(value, Path, str)
        self.__set_dir(value)

    def __set_dir(self, value: Union[Path, str]):
        path = Path(value).joinpath("logs")
        self.__dir = path
        self.__set_path(self.__dir, self.__name)

    @property
    def level(self) -> LogLevel:
        return self.__level

    @level.setter
    def level(self, value: L):
        _check_type(value, LogLevel, str, int)
        self.__set_level(value)

    def __set_level(self, value: L):
        if issubclass((v_type := type(value)), LogLevel):
            self.__level = value
        elif issubclass(v_type, str):
            self.__level = LogLevel.get_by_name(value.upper(), self.__level)
        elif issubclass(v_type, int):
            self.__level = LogLevel.get_by_value(value, self.__level)

    @property
    def level_console(self) -> LogLevel:
        return self.__level_console

    @level_console.setter
    def level_console(self, value: L):
        _check_type(LogLevel, str, int)
        self.__set_level_console(value)

    def __set_level_console(self, value: L):
        if issubclass(v_type := type(value), LogLevel):
            self.__level_console = value
        elif issubclass(v_type, str):
            self.__level_console = LogLevel.get_by_value(value.upper(), LogLevel.CRITICAL)
        elif issubclass(v_type, int):
            self.__level_console = LogLevel.get_by_name(value.upper(), LogLevel.CRITICAL)

    @property
    def level_file(self) -> LogLevel:
        return self.__level_file

    @level_file.setter
    def level_file(self, value: L):
        _check_type(value, LogLevel, str, int)
        self.__set_level_file(value)

    def __set_level_file(self, value: L):
        if issubclass(v_type := type(value), LogLevel):
            self.__level_file = value
        elif issubclass(v_type, str):
            self.__level_file = LogLevel.get_by_name(value.upper(), LogLevel.CRITICAL)
        elif issubclass(v_type, int):
            self.__level_file = LogLevel.get_by_value(value, LogLevel.CRITICAL)

    @property
    def format(self) -> Optional[str]:
        return self.__format

    @format.setter
    def format(self, value: Optional[str]):
        _check_type(value, str)
        self.__set_format(value)

    def __set_format(self, value: Optional[str]):
        if issubclass(type(value), str):
            self.__format = value

    @property
    def coding(self) -> Optional[str]:
        return self.__coding

    @coding.setter
    def coding(self, value: Optional[str]):
        self.__set_coding(value)

    def __set_coding(self, value: Optional[str]):
        if issubclass(type(value), str):
            self.__coding = value

    @property
    def name(self) -> str or Path:
        return self.__name

    @name.setter
    def name(self, value: str or Path):
        """
        will add date as suffix.
        Example:
            LogConfig.name = demo.log
            print(LogConfig.name) = demo-xxxx-xx-xx.log
        """
        self.__set_name(value)

    def __set_name(self, value: str or Path):
        if issubclass(type(value), (str, Path)):
            self.__name = Path(value)
            self.__set_path(self.dir, value)

    @property
    def rotating_when(self) -> str:
        return self.__rotating_when

    @rotating_when.setter
    def rotating_when(self, value: str):
        """
        "S": Second
        "M": Minutes
        "H": Hour
        "D": Days Day
        "W": Week day (0 = Monday)(0-6)
        "midnight": Roll over at midnight, default.
        when cut_mode = 0 used.
        """
        if issubclass(type(value), str):
            self.__rotating_when = value.upper()

    @property
    def cut_mode(self) -> int:
        return self.__cut_mode

    @cut_mode.setter
    def cut_mode(self, value: int):
        """
        Cut the pattern of the log
        1 - by time cut
        2 - by size cut
        """
        if issubclass(type(value), int):
            self.__cut_mode = value

    @property
    def backup_count(self) -> Optional[int]:
        return self.__backup_count

    @backup_count.setter
    def backup_count(self, value: Optional[int]):
        """
        Maximum number of shards
        default 30.
        when cut_mode = 1 used.
        """
        self.__set_backup_count(value)

    def __set_backup_count(self, value: Optional[int]):
        if issubclass(type(value), int):
            self.__backup_count = value

    @property
    def max_bytes(self) -> Optional[int]:
        return self.__max_bytes

    @max_bytes.setter
    def max_bytes(self, value: Optional[int]):
        """
        RotatingFileHandler mode, the maximum size of each file
        default size 100M.
        """
        self.__set_max_bytes(value)

    def __set_max_bytes(self, value: Optional[int]):
        if issubclass(type(value), int):
            self.__max_bytes = value

    @property
    def delay(self) -> bool:
        return self.__delay

    @delay.setter
    def delay(self, delay: bool):
        """
        If delay is true, then file opening is deferred until the first call to emit().
        By default, the file grows indefinitely.
        """
        self.__set_delay(delay)

    def __set_delay(self, value: bool):
        if isinstance(value, bool):
            self.__delay = value

    @property
    def path(self) -> Optional[Path]:
        """
        get log file full path,
        """
        return self.__path

    def __set_path(self, root: Path, name):
        self.__path = root.joinpath(name).absolute()

    @property
    def off_banner(self) -> Optional[bool]:
        return self.__off_banner

    @off_banner.setter
    def off_banner(self, value: B):
        """
        If False will not output banner.
        default False.
        env SB_BANNER_OFF also off of open banner
        """
        self.__set_off_banner(value)

    def __set_off_banner(self, value: B):
        if issubclass(v_type := type(value), bool):
            self.__off_banner = value
        elif issubclass(v_type, str):
            self.__off_banner = StringUtils.to_bool(value, True)

    @property
    def off_file(self) -> Optional[bool]:
        return self.__off_file

    @off_file.setter
    def off_file(self, value: B):
        """
        If false, no log will be output in the file
        default True

        If off is false, the off_console and off_file will be verified
        """
        self.__set_off_file(value)

    def __set_off_file(self, value: B):
        if issubclass(v_type := type(value), bool):
            self.__off_file = value
        elif issubclass(v_type, str):
            self.__off_file = StringUtils.to_bool(value, False)

    @property
    def off_console(self) -> Optional[bool]:
        return self.__off_console

    @off_console.setter
    def off_console(self, value: B):
        """
        If false, no log will be output in the console
        default  False.

        If off is false, the off_console and off_file will be verified
        """
        self.__set_off_console(value)

    def __set_off_console(self, value: B):
        if issubclass(v_type := type(value), bool):
            self.__off_console = value
        elif issubclass(v_type, str):
            self.__off_console = StringUtils.to_bool(value, False)

    @property
    def off(self) -> Optional[bool]:
        return self.__off

    @off.setter
    def off(self, value: B):
        """
        If false, no log will be generated, including file and console.
        default True.

        If off is false, the off_console and off_file will be verified
        """
        self.__set_off(value)

    def __set_off(self, value: B):
        if issubclass(v_type := type(value), bool):
            self.__off = value
        elif issubclass(v_type, str):
            self.__off = StringUtils.to_bool(value, False)


LogConfig: __LogConfig = __LogConfig()

__all__ = [LogConfig, LogLevel]
