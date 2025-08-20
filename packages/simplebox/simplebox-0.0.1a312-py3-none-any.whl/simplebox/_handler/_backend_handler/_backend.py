#!/usr/bin/env python
# -*- coding:utf-8 -*-
import builtins
import inspect
import os
import pickle
import platform
import warnings
from locale import getpreferredencoding
from pathlib import Path
from subprocess import Popen, PIPE
from sys import executable
from tempfile import gettempdir
from collections.abc import Iterable

from collections.abc import Callable
from ...character import StringBuilder
from ...config.log import LogConfig
from ...log import LoggerFactory
from ...utils.objects import ObjectsUtils
from ...utils.strings import StringUtils
from ...classes import Final
from ._run import _BackendRunner


_LOGGER = LoggerFactory.get_logger("backend")

_INNER_TYPE = dir(builtins)

_RUN_MODULE_NAME = _BackendRunner.__name__
_INIT_FILE_NAME = str(Path(__file__).parent.parent.parent.joinpath("backend.py"))


class _Backend(metaclass=Final):
    """
    Create a new process and then run it in background mode
    """

    def __init__(self, func: Callable, args: Iterable = None, kwargs: dict = None, log_path: str or Path = None):
        ObjectsUtils.call_limit(_INIT_FILE_NAME, ('backend_run', ))
        self.__all_args = (args or [], kwargs or {})
        self.__message_builder = StringBuilder()
        self.__message_builder.append(f"Backend run [{platform.system()}]: ")
        if not issubclass(type(func), Callable):
            raise TypeError(f"expected is function, got a {type(func).__name__}")
        self.__func_name = func.__name__
        self.__func = func
        if self.__func_name == "<lambda>":
            raise TypeError("cannot be a lambda function")
        self.__log_path = None
        if log_path and issubclass(type(log_path), (str, Path)):
            p = Path(log_path)
            if not p.is_absolute():
                self.__log_path = LogConfig.dir.joinpath(log_path)
            else:
                self.__log_path = p
        self.__frame = inspect.stack()[2]
        self.__run_path = Path(self.__frame[1]).parent
        self.__module_name = Path(self.__frame[1]).stem
        if "-" in self.__module_name:
            raise ImportError(f"Module names cannot contain hyphens '-', error module: {self.__module_name}")
        # When find for processes, you can filter by filtering the keywords in commandline (flag here).
        self.__flag = f"simplebox-backend-run-{os.getpid()}-{self.__module_name}-{self.__func_name}-{ObjectsUtils.generate_random_str(6)}"
        self.__fifo_file = Path(gettempdir()).joinpath(f"simplebox-backend-fifo-{os.getpid()}-{self.__module_name}-{self.__func_name}-{ObjectsUtils.generate_random_str(6)}").absolute()

        self.__python_statement = StringBuilder(sep=" ", start='"', end='"')

        def import_module(modules: Iterable):
            for module in modules:
                if inspect.ismodule(module):
                    self.__python_statement.append("import").append(module.__name__ + ";")
                elif inspect.isfunction(module):
                    self.__python_statement.append("from").append(module.__module__) \
                        .append("import").append(module.__name__ + ";")
                elif inspect.isclass(module.__class__):
                    att_name = type(module).__name__
                    if att_name not in _INNER_TYPE:
                        if module.__module__ == "__main__":
                            self.__python_statement.append("from").append(self.__module_name) \
                                .append("import").append(module.__class__.__name__ + ";")
                        else:
                            self.__python_statement.append("from").append(module.__module__) \
                                .append("import").append(module.__class__.__name__ + ";")

        import_module(self.__all_args[0])
        import_module(self.__all_args[1].values())

        self.__python_statement.append("from") \
            .append(self.__module_name) \
            .append("import") \
            .append(self.__func_name + ";") \
            .append(f"from") \
            .append(_BackendRunner.__module__) \
            .append("import") \
            .append(_RUN_MODULE_NAME) \
            .append(";") \
            .append(f"{_RUN_MODULE_NAME}(r'{str(self.__fifo_file)}', {self.__func_name})") \
            .append(" #").append(self.__flag)

    def __enter__(self):
        self.__fifo = open(self.__fifo_file, "w+b")
        pickle.dump(self.__all_args, self.__fifo, 0)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__fifo.close()

    def runner(self):
        os_name = os.name
        exec_func_name = f"_Backend__run_{os_name.lower()}_cmd"
        exec_func = getattr(self, exec_func_name, None)
        if callable(exec_func):
            exec_func()
            self.__message_builder.append(";").append(f"process tag => {self.__flag}")
            _LOGGER.log(level=10, msg=self.__message_builder.string(), stacklevel=3)
        else:
            raise RuntimeError(f"Unsupported operating systems: {os_name}")

    def __run_nt_cmd(self):
        """
        windows run
        """
        cmd = StringBuilder(sep=" ")
        cmd.append(executable) \
            .append("-c") \
            .append(self.__python_statement.string())
        if self.__log_path:
            cmd.append(">>").append(self.__log_path)
        self.__sub_process(cmd.string())
        self.__get_pid_nt()

    def __run_posix_cmd(self):
        """
        unix-like run
        """
        cmd = StringBuilder(sep=" ")
        cmd.append("nohup") \
            .append(executable) \
            .append("-c") \
            .append(self.__python_statement.string())
        if self.__log_path:
            cmd.append(">").append(self.__log_path).append("2>&1 &")
        else:
            cmd.append("/dev/null")
        cmd.append("2>&1 &")
        self.__sub_process(cmd.string())
        self.__get_pid_unix()

    def __get_pid_nt(self):
        cmd = StringBuilder(sep=" ")
        cmd.append("wmic") \
            .append("process") \
            .append("where") \
            .append("\"") \
            .append("commandline") \
            .append("like") \
            .append(f"'%%{self.__flag}%%'") \
            .append("and") \
            .append("name") \
            .append("!=") \
            .append("'WMIC.exe'") \
            .append("and") \
            .append("name") \
            .append("like") \
            .append("'python%'") \
            .append("\"") \
            .append("get") \
            .append("processid")
        process = Popen(cmd.string(), shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                        encoding=getpreferredencoding(False))
        out, err = process.communicate()
        if process.returncode == 0 and "ProcessId" in out:
            message = StringUtils.trip(out.split('ProcessId')[1])
        else:
            message = f"error: {StringUtils.trip(err)}"
        self.__message_builder.append(f"Pid => {message}")

    def __get_pid_unix(self):
        cmd = StringBuilder(sep=" ")
        cmd.append("ps") \
            .append("-ef") \
            .append("|") \
            .append("grep") \
            .append("-v") \
            .append("grep") \
            .append("|") \
            .append("grep") \
            .append("-w") \
            .append(self.__flag) \
            .append("|") \
            .append("awk") \
            .append("'{print $2}'")
        process = Popen(cmd.string(), shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                        encoding=getpreferredencoding(False))
        out, err = process.communicate()
        if StringUtils.is_not_empty(out):
            message = StringUtils.trip(out)
        else:
            message = f"error: {StringUtils.trip(err)}"
        self.__message_builder.append(f"Pid => {message}")

    def __sub_process(self, cmd: str):
        warnings.simplefilter("ignore", ResourceWarning)
        Popen(cmd, cwd=self.__run_path, shell=True)
