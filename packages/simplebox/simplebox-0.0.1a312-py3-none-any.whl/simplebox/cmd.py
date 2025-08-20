#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import inspect
from abc import ABCMeta, abstractmethod

from locale import getpreferredencoding
from pathlib import Path
from subprocess import PIPE, Popen, run
from typing import Any
from collections.abc import Callable

from .character import String, StringBuilder
from .classes import StaticClass
from .exceptions import raise_exception
from .exceptions import EmptyException, CommandException
from .log import LoggerFactory
from .utils.objects import ObjectsUtils
from .utils.strings import StringUtils
from . import sjson as json

_LOGGER = LoggerFactory.get_logger("command")

_ENCODING = getpreferredencoding(False)


class Command(StaticClass):
    """
    Command-line utility classes.
    Two execution methods are provided, one is runtime (native subprocess.run).
    The other is the exec execution method of this tool extension, which supports the input of interactive instructions.
    """

    @staticmethod
    def exec(cmd, cwd: str or Path = None, timeout: int = None, encoding: str = None, **kwargs) -> 'CommandAdvice':
        """
        The execute command can enter interactive instructions through the input method before calling finish.
        :param encoding: encode
        :param cmd: commandline
        :param cwd: working directory
        :param timeout: timeout, default block thread

        Usage:
            Command.exec("rm -r /tmp/tmp").input("y").finish()
        """
        return CommandExecutor(cmd, cwd=cwd, timeout=timeout, encoding=encoding, **kwargs)

    @staticmethod
    def executed(cmd, cwd: str or Path = None, timeout: int = None, encoding: str = None, **kwargs) \
            -> 'CommandAdvice':
        """
        Quickly execute the command and return the result. The function assumes no interaction input.
        Function executed can meet most usage scenarios.
        Usage:
            Command.executed("ls") like use Command.exec("ls").finish()
        """
        return Command.exec(cmd, cwd, timeout, encoding, **kwargs).finish()

    @staticmethod
    def run(*popenargs, cwd: str or Path = None, input=None, capture_output=False, timeout=None, check=False,
            encoding: str = None, **kwargs) -> 'CommandAdvice':
        """
        subprocess run method
        """
        return CommandRunner(*popenargs, cwd=cwd, input=input, capture_output=capture_output, timeout=timeout,
                             check=check, encoding=encoding, **kwargs)

    @staticmethod
    def runned(*popenargs, cwd: str or Path = None, input=None, capture_output=False, timeout=None, check=False,
               encoding: str = None, **kwargs) -> 'CommandAdvice':
        """
        Quickly execute the subprocess run and return the result.
        """
        return Command.run(*popenargs, cwd=cwd, input=input, capture_output=capture_output, timeout=timeout,
                           check=check, encoding=encoding, **kwargs).finish()


class CommandPrivate(StaticClass):
    """
    Don't show command log, and other's feature is the same as #{Command}.
    """

    @staticmethod
    def exec(cmd, cwd: str or Path = None, timeout: int = None, encoding: str = None, **kwargs) -> 'CommandAdvice':
        """
        The execute command can enter interactive instructions through the input method before calling finish.
        :param encoding: encode
        :param cmd: commandline
        :param cwd: working directory
        :param timeout: timeout, default block thread

        Usage:
            CommandPrivate.exec("rm -r /tmp/tmp").input("y").finish()
        """
        return CommandExecutor(cmd, cwd=cwd, timeout=timeout, encoding=encoding, show_log=False, **kwargs)

    @staticmethod
    def executed(cmd, cwd: str or Path = None, timeout: int = None, encoding: str = None, **kwargs) \
            -> 'CommandAdvice':
        """
        Quickly execute the command and return the result. The function assumes no interaction input.
        Function executed can meet most usage scenarios.
        Usage:
            CommandPrivate.executed("ls") like use CommandPrivate.exec("ls").finish()
        """
        return CommandPrivate.exec(cmd, cwd, timeout, encoding, **kwargs).finish()

    @staticmethod
    def run(*popenargs, cwd: str or Path = None, input=None, capture_output=False, timeout=None, check=False,
            encoding: str = None, **kwargs) -> 'CommandAdvice':
        """
        subprocess run method
        """
        return CommandRunner(*popenargs, cwd=cwd, input=input, capture_output=capture_output, timeout=timeout,
                             check=check, encoding=encoding, show_log=False, **kwargs)

    @staticmethod
    def runned(*popenargs, cwd: str or Path = None, input=None, capture_output=False, timeout=None, check=False,
               encoding: str = None, **kwargs) -> 'CommandAdvice':
        """
        Quickly execute the subprocess run and return the result.
        """
        return CommandPrivate.run(*popenargs, cwd=cwd, input=input, capture_output=capture_output, timeout=timeout,
                                  check=check, encoding=encoding, **kwargs).finish()


class CommandAdvice(metaclass=ABCMeta):

    def __setattr__(self, key, value):
        if __file__ != inspect.stack()[1].filename:
            return
        self.__dict__[key] = value

    def __init__(self, kwargs: dict[str, Any], show_log: bool = True):
        self.__cmd = None
        self.__cwd = None
        self.start_time = None
        self.end_time = None
        self.__code: int = -1
        self.__err_dict = {}
        self.__out_dict = {}
        self.__out = ""
        self.__err = ""
        if "stdin" not in kwargs:
            kwargs["stdin"] = PIPE
        if "stdout" not in kwargs:
            kwargs["stdout"] = PIPE
        if "stderr" not in kwargs:
            kwargs["stderr"] = PIPE
        self.__show_log = show_log
        self.__input_log_builder: StringBuilder = StringBuilder(start="\n")

    def __showing_log(self):
        input_msg = self.__input_log_builder.string(lambda i, v: f'\t({i}) interactive input => {v}\n')
        timing = self.end_time - self.start_time
        log_content = f"""
{'Command START'.center(81, '*')}
Command line              => {self.__cmd}\n
Command work dir          => {self.__cwd}
{'' if StringUtils.is_empty(input_msg) else input_msg}
Command exit code         => {self.__code}\n
Command out               => \n{self.__out}\n
Command err               => \n{self.__err}\n
Command start time        => {self.start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}\n
Command end time          => {self.end_time.strftime('%Y-%m-%d %H:%M:%S.%f')}\n
Command consume time         => {(timing.microseconds / 1000):.3f} millisecond(s)\n
{'Command END'.center(83, '*')}
"""
        _LOGGER.log(level=10, msg=log_content, stacklevel=3)

    @abstractmethod
    def input(self, line: str) -> 'CommandAdvice':
        raise NotImplementedError()

    @abstractmethod
    def finish(self) -> 'CommandAdvice':
        if self.__show_log:
            self.__showing_log()
        return self

    def build_log_meta(self, cmd, cwd, code: int, out: str, err: str):
        self.__cmd = cmd
        self.__cwd = cwd
        self.__code = code
        self.__out: str = ObjectsUtils.none_of_default(out, "")
        self.__err: str = ObjectsUtils.none_of_default(err, "")
        # noinspection PyBroadException
        try:
            self.__out_dict = json.loads(self.__out)
        except BaseException:
            pass
        # noinspection PyBroadException
        try:
            self.__err_dict = json.loads(self.__err)
        except BaseException:
            pass

    @property
    def args(self):
        return self.__cmd

    @property
    def code(self) -> int:
        """
        Returns the exit code after executing the command
        """
        return self.__code

    @property
    def out(self) -> String:
        """
        Returns standard output
        """
        return String(self.__out)

    @property
    def out_to_dict(self) -> dict:
        """
        Converts command-line standard output to dict
        """
        return self.__out_dict

    @property
    def err(self) -> String:
        """
        Returns standard error
        """
        return String(self.__err)

    @property
    def err_to_dict(self) -> dict:
        """
        Convert command-line standard error to dict
        """
        return self.__out_dict

    @property
    def is_success(self) -> bool:
        """
        Determine whether the command line is executed successfully
        """
        return self.__code == 0

    @property
    def is_fail(self) -> bool:
        """
        Determine whether the command line is executed failed
        """
        return not self.is_success

    @property
    def out_is_empty(self) -> bool:
        """
        Determine whether the standard output is blank
        """
        return StringUtils.is_empty(self.__out)

    @property
    def out_is_not_empty(self) -> bool:
        """
        Judge that the standard output is not blank
        """
        return not self.out_is_empty

    def out_contain(self, value: Any) -> bool:
        """
        Judge that the standard output contains a value
        """
        return StringUtils.contains(self.__out, str(value))

    def out_not_contain(self, value: Any) -> bool:
        """
        The criterion output does not contain a value
        """
        return not self.out_contain(str(value))

    def out_trip_contain(self, value: Any) -> bool:
        """
        Judgment standard output contains values (after removing leading and trailing spaces)
        """
        return StringUtils.trip_contains(self.__out, str(value))

    def out_trip_not_contain(self, value: Any) -> bool:
        """
        Judgment standard output does not contain values (after removing leading and trailing spaces)
        """
        return not self.out_trip_contain(str(value))

    def out_equal(self, value: Any) -> bool:
        """
        Judge that the standard output is equal to the value
        """
        return str(value) == self.__out

    def out_not_equal(self, value: Any) -> bool:
        """
        Determine that the standard output is not equal to the value
        """
        return not self.out_equal(str(value))

    def out_trip_equal(self, value: Any) -> bool:
        """
        Judge that the standard output is equal to the value (after removing the leading and trailing spaces)
        """
        return str(value).strip() == self.__out.strip()

    def out_trip_not_equal(self, value: Any) -> bool:
        """
        Judge that the standard output is not equal to the value (after removing the leading and trailing spaces)
        """
        return not self.out_trip_equal(str(value))

    @property
    def err_is_empty(self) -> bool:
        """
        The criterion error is blank
        """
        return StringUtils.is_empty(self.__err)

    @property
    def err_is_not_empty(self) -> bool:
        """
        Criterion errors are not blank
        """
        return not self.err_is_empty

    def err_contain(self, value: Any) -> bool:
        """
        The criterion error contains a value
        """
        return StringUtils.contains(self.__err, str(value))

    def err_not_contain(self, value: Any) -> bool:
        """
        The criterion error does not contain a value
        """
        return not self.err_contain(str(value))

    def err_trip_contain(self, value: Any) -> bool:
        """
        Judgment criterion error contains value (after removing leading and trailing spaces)
        """
        return StringUtils.trip_contains(self.__err, str(value))

    def err_trip_not_contain(self, value: Any) -> bool:
        """
        Criterion error does not contain a value (after removing leading and trailing spaces)
        """
        return not self.err_trip_contain(str(value))

    def err_equal(self, value: Any) -> bool:
        """
        The criterion error is equal to the value
        """
        return str(value) == self.__err

    def err_not_equal(self, value: Any) -> bool:
        """
        The criterion error is not equal to the value
        """
        return not self.err_equal(str(value))

    def err_trip_equal(self, value: Any) -> bool:
        """
        The criterion error is equal to the value (after removing the leading and trailing spaces)
        """
        return str(value).strip() == self.__err.strip()

    def err_trip_not_equal(self, value: Any) -> bool:
        """
        The criterion error is not equal to the value (after removing the leading and trailing spaces, it is judged)
        """
        return not self.err_trip_equal(str(value))

    def check(self, predicate: Callable[['CommandAdvice'], bool],
              exception: BaseException = CommandException("command result check failed.")):
        """
        Check the results
        :param predicate: the callback function for the validation result
        :param exception: check fail raise exception
        :return:
        """
        if not predicate(self):
            raise_exception(exception)

    def check_success(self):
        """
        check command returncode is 0
        """
        self.check(lambda result: result.is_success,
                   CommandException(f"command returncode is '{self.code}', check failed."))


class CommandExecutor(CommandAdvice):
    def __init__(self, cmd, cwd: Path or str = None, timeout: int = None, encoding: str = None, show_log: bool = True,
                 **kwargs):
        super().__init__(kwargs, show_log=show_log)
        self.__is_finish = False
        self.__cmd, self.__cwd = cmd, ObjectsUtils.none_of_default(cwd, Path.cwd())
        self.__process = Popen(cmd, cwd=self.__cwd, shell=True,
                               universal_newlines=True,
                               encoding=ObjectsUtils.none_of_default(encoding, _ENCODING), **kwargs)
        self.__timeout: int = timeout if issubclass(type(timeout), int) and timeout > 0 else None

    def input(self, content: str) -> 'CommandAdvice':
        if not isinstance(content, str):
            raise TypeError("need str type params")
        getattr(self, f"_{CommandAdvice.__name__}__input_log_builder").append(content)
        self.__process.stdin.write(content)
        self.__process.stdin.write("\n")
        self.__process.stdin.flush()
        return self

    def finish(self) -> 'CommandAdvice':
        if self.__is_finish:
            raise EmptyException("commend is finished.")
        self.__is_finish = True
        self.start_time = datetime.datetime.now()
        out, err = self.__process.communicate(timeout=self.__timeout)
        self.end_time = datetime.datetime.now()
        self.build_log_meta(self.__cmd, self.__cwd, self.__process.returncode, out, err)
        self.__process.stdin.close()
        super(CommandExecutor, self).finish()
        return self


class CommandRunner(CommandAdvice):
    def __init__(self, *popenargs, cwd: str or Path = None, input=None, capture_output=False, timeout=None,
                 check=False, encoding: str = _ENCODING, show_log: bool = True, **kwargs):
        super().__init__(kwargs, show_log=show_log)
        self.__is_finish = False
        kwargs["shell"] = True
        kwargs["cwd"] = ObjectsUtils.none_of_default(cwd, Path.cwd())
        kwargs["input"] = input
        kwargs["capture_output"] = capture_output
        kwargs["timeout"] = timeout
        kwargs["check"] = check
        self.__cwd = kwargs["cwd"]
        encoding = ObjectsUtils.none_of_default(encoding, _ENCODING)
        self.start_time = datetime.datetime.now()
        self.__result = run(*popenargs, encoding=encoding, **kwargs)
        self.end_time = datetime.datetime.now()

    def input(self, line: str) -> 'CommandAdvice':
        raise NotImplementedError("CommandRunner error: interactive input is not supported.")

    def finish(self) -> 'CommandAdvice':
        if self.__is_finish:
            raise EmptyException("commend is finished.")
        self.__is_finish = True
        self.build_log_meta(self.__result.args, self.__cwd,
                            self.__result.returncode,
                            self.__result.stdout,
                            self.__result.stderr)
        super(CommandRunner, self).finish()
        return self


__all__ = [CommandAdvice, Command, CommandPrivate]

