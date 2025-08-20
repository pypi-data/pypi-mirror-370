#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import traceback
from functools import wraps
from logging import Formatter, Logger, LoggerAdapter
from platform import system
from sys import exc_info
from threading import current_thread

from ._handler import _TimedRotatingFileHandlerWrapper, _RotatingFileHandlerWrapper, _StreamHandlerWrapper
from .. import banner
from .._handler._method_handler._build_arguments import _arguments_to_parameters
from ..cache import CacheManager
from ..classes import ForceType
from ..config.log import LogConfig, LogLevel
from ._filter import _SimpleLogFilter
from ..generic import V, T
from ..singleton import SingletonMeta
from ..utils.strings import StringUtils
from ..utils.objects import ObjectsUtils

from ..log import _TRACE_ID_KEY

__all__ = []


CacheManager.put(_TRACE_ID_KEY, {})
_WINDOWS_LOGGER = None
_PLATFORM_NAME = system()
_PLATFORM_WINDOWS = "Windows"


class _LoggerWrapper(Logger):
    """
    Log wrapper.
    Provides logging processing.
    """
    __level = ForceType(LogLevel)
    __level_file = ForceType(LogLevel)
    __level_console = ForceType(LogLevel)

    def __init__(self, name: str, level: LogLevel, level_file: LogLevel, level_console: LogLevel):
        self.__level = level
        self.__level_file = level_file
        self.__level_console = level_console
        super().__init__(name, self.__level.value)
        self.__initialize()

    def __initialize(self):
        if not LogConfig.off and not LogConfig.off_file and not LogConfig.dir.exists():
            LogConfig.dir.mkdir(parents=True)
        if not LogConfig.off:
            if not LogConfig.off_console:
                self.__build_stream_handler()
            if not LogConfig.off_file:
                self.__build_file_handler()
        self.setLevel(self.__level.value)

    def __build_stream_handler(self):
        handler = _StreamHandlerWrapper()
        level_filter = _SimpleLogFilter(self.__level_console if self.__level_console else LogLevel.CRITICAL)
        handler.addFilter(level_filter)
        handler.setLevel(LogConfig.level.value)
        handler.setFormatter(Formatter(LogConfig.format))
        self.addHandler(handler)

    def __build_file_handler(self):
        if not LogConfig.dir.exists():
            LogConfig.dir.mkdir(parents=True, exist_ok=True)
        cut_mode = LogConfig.cut_mode
        if cut_mode == 1:
            handler = _TimedRotatingFileHandlerWrapper(filename=str(LogConfig.path),
                                                       encoding=LogConfig.coding,
                                                       when=LogConfig.rotating_when,
                                                       backupCount=LogConfig.backup_count,
                                                       delay=LogConfig.delay)

        elif cut_mode == 2:
            handler = _RotatingFileHandlerWrapper(filename=str(LogConfig.path),
                                                  encoding=LogConfig.coding,
                                                  maxBytes=LogConfig.max_bytes,
                                                  backupCount=LogConfig.backup_count,
                                                  delay=LogConfig.delay)
        else:
            raise ValueError(f"Log Error: unknown cut mode: {cut_mode}, Expected '1, 2'")
        level_filter = _SimpleLogFilter(self.__level_file if self.__level_file else LogLevel.CRITICAL)
        handler.addFilter(level_filter)
        handler.setLevel(LogConfig.level.value)
        handler.setFormatter(Formatter(LogConfig.format))
        self.addHandler(handler)


class _LoggerAdapterWrapper(LoggerAdapter):

    def __init__(self, name: str, level: LogLevel, level_file: LogLevel, level_console: LogLevel):
        self.__trace_root_cause = None
        if _PLATFORM_NAME == _PLATFORM_WINDOWS:
            global _WINDOWS_LOGGER
            if not _WINDOWS_LOGGER:
                super().__init__(_WINDOWS_LOGGER := _LoggerWrapper("root", LogConfig.level, LogConfig.level_file,
                                                                   LogConfig.level_console), {})
            else:
                super().__init__(_WINDOWS_LOGGER, {})
        else:
            super().__init__(_LoggerWrapper(name, level, level_file, level_console), {})

    def runlog(self):
        """
        print log when run function before and after.
        The difference from simplelog is that simplelog only prints one line (which also contains the
        function execution status), and runlog prints log before and after execution respectively.
        :return:
        """
        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                result = None
                parameters = _arguments_to_parameters(func, args, kwargs)
                temp = f"'{func.__name__}' before running,  parameters={parameters}"
                self.info(temp)
                try:
                    result = func(*args, **kwargs)
                    return result
                except BaseException as e:
                    raise e
                finally:
                    temp = f"'{func.__name__}' after running,  return: {result}"
                    self.info(temp)
            return __wrapper
        return __inner

    def trace(self, value: V = None) -> T:
        """
        Set up tracking points
        :param value: trace id
        :return:
        """

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                if not value:
                    _value = ObjectsUtils.generate_random_str(16)
                else:
                    _value = value
                set_ok = self.__set(_value)
                try:
                    return func(*args, **kwargs)
                except BaseException as e:
                    if self.__trace_root_cause is None:
                        _, exec_val, _ = exc_info()
                        self.__trace_root_cause = f"{e.__class__.__name__}: {exec_val}"
                    msg = f"\nEXCEPTION TRACE: {self.get_trace_id()}\n{'EXCEPTION STACK'.center(35, '*')}"
                    self.critical(f"{msg}\n{traceback.format_exc()}")
                    raise Exception(f"[TRACE {self.get_trace_id()}]: {self.__trace_root_cause}")
                finally:
                    if set_ok:
                        self.__remove()

            return __wrapper

        return __inner

    def catch(self, exception: type[BaseException] = BaseException, flag: str = "") -> T:
        """
        catch exception when function runtime happened exception.
        :param flag: content flag.
        :param exception: The exception base class catches
        if the exception occurs if it is a subclass of that exception type, otherwise it does not matter.
        example:
            @log.catch()
            def test_exception(a, b, c=3, d=4):
                return 'test result'

        """

        def __inner(func):
            @wraps(func)
            def __wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    return result
                except BaseException as e:
                    if issubclass(type(e), exception):
                        self.log(level=LogLevel.ERROR.value, msg=f"{flag} => \n{traceback.format_exc()}", stacklevel=3)

            return __wrapper

        return __inner

    @staticmethod
    def __set(value: V) -> bool:
        key = current_thread().ident
        trace_id_map = CacheManager.get_data(_TRACE_ID_KEY)
        if key and key not in trace_id_map:
            trace_id_map[key] = value
            return True
        return False

    @staticmethod
    def get_trace_id(default: V = None) -> V:
        key = current_thread().ident
        trace_id_map = CacheManager.get_data(_TRACE_ID_KEY)
        return trace_id_map.get(key, default)

    @staticmethod
    def __remove():
        key = current_thread().ident
        trace_id_map = CacheManager.get_data(_TRACE_ID_KEY)
        if key in trace_id_map:
            del trace_id_map[key]


class _LoggerFactory(metaclass=SingletonMeta):

    def __init__(self):
        tmp_off_console = LogConfig.off_console
        LogConfig.off_console = True
        self.__show_banner()
        LogConfig.off_console = tmp_off_console
        global _WINDOWS_LOGGER
        _WINDOWS_LOGGER = None

    def __show_banner(self):
        if StringUtils.to_bool(os.getenv("SB_BANNER_OFF", False), False):
            return
        if LogConfig.off_banner:
            return
        log = self.get_logger()
        content = banner
        from .._internal import _banner
        for info in getattr(_banner, "__build_frame_banner_infos")():
            init_len = 200
            split_len = 32
            key_len = 20
            value_len = 0
            left_len = 4
            logo = info['title']
            logo_len = len(logo)
            content += f"""
{''.center(init_len, "#")}
{'#'.ljust(int((init_len - logo_len) / 2), " ")}{logo}{'#'.rjust(int((init_len - logo_len) / 2), " ")}
"""
            banner_dict = info['properties']
            for k, v in banner_dict.items():
                v_ = str(v)
                line = f"{k.ljust(key_len)}{'=>'.center(split_len, ' ')}{v_.rjust(value_len)}"
                content += f"{'#'.ljust(left_len, ' ')}{line}{'#'.rjust(init_len - len(line) - left_len, ' ')}\n"

            content += f"{''.center(init_len, '#')}"
        log.info(content)

    @staticmethod
    def get_logger(name: str = "root", level: LogLevel = LogConfig.level, level_file: LogLevel = LogConfig.level_file,
                   level_console: LogLevel = LogConfig.level_console) -> '_LoggerAdapterWrapper':
        """
        get a logger.
        if windows platform, logger will a singleton,
        and level, level_file, level_console will use LogConfig value, name will always show 'root'.
        """
        if StringUtils.is_empty(name):
            name_ = "root"
        else:
            name_ = name
        if not issubclass(type(level), LogLevel):
            level_ = LogConfig.level
        else:
            level_ = level
        if not issubclass(type(level_file), LogLevel):
            level_file_ = LogConfig.level_file
        else:
            level_file_ = level_file
        if not issubclass(type(level_console), LogLevel):
            level_console_ = LogConfig.level_console
        else:
            level_console_ = level_console
        return _LoggerAdapterWrapper(name_, level_, level_file_, level_console_)


LoggerFactory = _LoggerFactory()
