#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import traceback
from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser, _SubParsersAction

from ..config.json import JsonConfig
from ..config.log import LogConfig, LogLevel
from ..config.property import PropertyConfig
from ..config.rest import RestConfig
from ..config.serialize import SerializeConfig

__all__ = ['init']

_level_choices = LogLevel.get_keys()


class BaseArgParse(metaclass=ABCMeta):

    @abstractmethod
    def parser(self):
        """
        parser args and execute action.
        :return:
        """


def _set_value(o, args):
    prefix = f"{o.__class__.__name__}__"
    for attr in o.__dict__:
        name = attr[len(prefix) - 1:]
        if hasattr(args, name):
            setattr(o, attr, getattr(args, name))


class __SimpleboxArgParse:

    def __init__(self):
        self.__parser = ArgumentParser(prog="simplebox",
                                       add_help=True,
                                       usage="python xxx.py --simplebox [logconfig|restconfig|propconfig|jsonconfig] --[option]=value",
                                       description="When the command line starts, "
                                                   "the configuration value of the simplebox.config module is provided."
                                                   "use 'python -m simplebox.config.show', can show all config.")
        self.__parser.add_argument("--simplebox", action="store_true", default=False,
                                   help="Whether to enable the simplebox option or not, "
                                        "the specified must be displayed before the simplebox command can be resolved. "
                                        "To avoid conflicts with command-line commands of other frameworks, "
                                        "do not use them with other command-line frameworks.")
        self.__subparsers = self.__parser.add_subparsers()

    def parser(self):
        if "--simplebox" not in sys.argv:
            return
        for config in BaseArgParse.__subclasses__():
            config(self.__subparsers).parser()
        all_args = sys.argv[1:]
        if "--simplebox" in all_args:
            all_args.remove("--simplebox")
        while all_args:
            args, tmp_all_args = self.__parser.parse_known_args(all_args)
            if set(tmp_all_args[:]) == set(all_args[:]):
                return
            all_args = tmp_all_args[:]
            if 'help' in args and args.help:
                self.__parser.print_help()

            if "func" in args:
                args.func(args)


class LogConfigParser(BaseArgParse):

    def __init__(self, action: _SubParsersAction):
        self.__parser = action.add_parser("logconfig", usage="logconfig --[dir|level|...]",
                                          description="log module configuration")

    def parser(self):
        self.__parser.add_argument("--dir", type=str, default=LogConfig.dir,
                                   help="The directory where the log is saved, the current working directory is "
                                        "the default directory.")
        self.__parser.add_argument("--level",
                                   type=str,
                                   choices=_level_choices,
                                   default=LogConfig.level,
                                   help="log level")
        self.__parser.add_argument("--level-file",
                                   type=str,
                                   choices=_level_choices,
                                   default=LogConfig.level_file,
                                   help="The filter level of the log when it is saved to a file.")
        self.__parser.add_argument("--level-console",
                                   type=str,
                                   choices=_level_choices,
                                   default=LogConfig.level_console,
                                   help="The filter level of the log when it is output to console.")
        self.__parser.add_argument("--format",
                                   type=str,
                                   default=LogConfig.format,
                                   help="Log output format.")
        self.__parser.add_argument("--coding", type=str, default=LogConfig.coding, help="Log encode code.")
        self.__parser.add_argument("--name", type=str, default=LogConfig.name,
                                   help="The name of the file when the log is exported to the file. "
                                        "The .log suffix is added by default")
        self.__parser.add_argument("--rotating-when",
                                   type=str,
                                   choices=['S', 'M', 'H', 'D', 'W', 'midnight'],
                                   default=LogConfig.rotating_when,
                                   help="Specifies the time unit for log file rotation. S: Second\nM: Minutes\nH: "
                                        "Hour\nD: Days Day\nW: Week day (0 = Monday)(0-6)\nmidnight: Roll over at "
                                        "midnight, default.\nwhen cut_mode = 0 used.")
        self.__parser.add_argument("--max-bytes", type=int, default=LogConfig.max_bytes,
                                   help="Specifies the file size of the cut log.")
        self.__parser.add_argument("--delay", action="store_true", default=LogConfig.delay,
                                   help="If the default mode is append, and if the delay is true, the file will "
                                        "not be opened until the emitting method is executed. By default, "
                                        "the log file can grow indefinitely.")
        self.__parser.add_argument("--cut-mode",
                                   type=int,
                                   choices=[1, 2],
                                   default=LogConfig.cut_mode,
                                   help="Cutting mode, 1. Cut by time. 2. Cut by file size.")
        self.__parser.add_argument("--backup-count", type=int, default=LogConfig.backup_count,
                                   help="Maximum number of backup files.")
        self.__parser.add_argument("--off-banner", action="store_true", default=LogConfig.off_banner,
                                   help="Turn off the simplebox label and configuration information at startup")
        self.__parser.add_argument("--off-file", action="store_true", default=LogConfig.off_file,
                                   help="It will not be output to a file.")
        self.__parser.add_argument("--off-console", action="store_true", default=LogConfig.off_console,
                                   help="It will not be output to console.")
        self.__parser.add_argument("--off", action="store_true", default=LogConfig.off, help="Close all log.")
        self.__parser.set_defaults(func=self.__to_config)

    @staticmethod
    def __to_config(args):
        _set_value(LogConfig, args)


class RestConfigParser(BaseArgParse):
    def __init__(self, action: _SubParsersAction):
        self.__parser = action.add_parser("restconfig", usage="restconfig --[allow-redirection|encoding|...]",
                                          description="log module configuration")

    def parser(self):
        self.__parser.add_argument("--allow-redirection", action="store_true", default=RestConfig.allow_redirection,
                                   help="Allow automatic redirects.")
        self.__parser.add_argument("--check-status", action="store_true", default=RestConfig.check_status,
                                   help="After the HTTP request is complete, check whether the http status is 2xx.")
        self.__parser.add_argument("--encoding", type=str, default=RestConfig.encoding,
                                   help="encode code.")
        self.__parser.add_argument("--http-log-level", type=str,
                                   choices=_level_choices,
                                   default=RestConfig.allow_redirection,
                                   help="This value is set only for the log of the REST module, if it is set.")
        self.__parser.set_defaults(func=self.__to_config)

    @staticmethod
    def __to_config(args):
        _set_value(RestConfig, args)


class PropertyConfigParser(BaseArgParse):
    def __init__(self, action: _SubParsersAction):
        self.__parser = action.add_parser("propconfig", usage="propconfig --[allow-redirection|encoding|...]",
                                          description="log module configuration")

    def parser(self):
        self.__parser.add_argument("--resources-dir", type=str, default=PropertyConfig.resources,
                                   help="Set the directory of the resource file.")
        self.__parser.set_defaults(func=self.__to_config)

    @staticmethod
    def __to_config(args):
        _set_value(PropertyConfig, args)


class JsonConfigParser(BaseArgParse):

    def __init__(self, action: _SubParsersAction):
        self.__parser = action.add_parser("jsonconfig", usage="jsonconfig --[newline|indent2|...]",
                                          description="sjson module global config.")

    def parser(self):
        self.__parser.add_argument("--newline", action="store_true", default=False,
                                   help="Append to the output. This is a convenience and optimization for the pattern of . objects are immutable and this pattern copies the original contents.\ndumps(...) + '\\n'bytes. default False.")
        self.__parser.add_argument("--indent2", action="store_true", default=False,
                                   help="Pretty-print output with an indent of two spaces. This is equivalent to in the standard library. Pretty printing is slower and the output larger. orjson is the fastest compared library at pretty printing and has much less of a slowdown to pretty print than the standard library does. This option is compatible with all other options.indent=2. default False.")
        self.__parser.add_argument("--naive-utc", action="store_true", default=False,
                                   help="Serialize objects without a as UTC. This has no effect on objects that have set.datetime.datetime tzinfo. default False.")
        self.__parser.add_argument("--non-str-keys", action="store_true", default=False,
                                   help="Serialize keys of type other than . This allows keys to be one of , , , , , , , , , and . For comparison, the standard library serializes , , , or by default. orjson benchmarks as being faster at serializing non- keys than other libraries. This option is slower for keys than the default. dict,str,int,float,bool,None,datetime.datetime,datetime.date,datetime.time,enum.Enum,uuid.UUID. default False.")
        self.__parser.add_argument("--omit-microseconds", action="store_true", default=False,
                                   help="Do not serialize the field on and instances.microsecond datetime.datetime datetime.time. default False.")
        self.__parser.add_argument("--passthrough-dataclass", action="store_true", default=False,
                                   help="Passthrough dataclasses.dataclass instances to default. This allows customizing their output but is much slower. default False.")
        self.__parser.add_argument("--passthrough-datetime", action="store_true", default=False,
                                   help="Passthrough dataclasses.dataclass instances to default. This allows customizing their output but is much slower. default False.")
        self.__parser.add_argument("--passthrough-subclass", action="store_true", default=False,
                                   help="Passthrough subclasses of builtin types to default. default False.")
        self.__parser.add_argument("--serialize-dataclass", action="store_true", default=False,
                                   help="This is deprecated and has no effect in version 3. In version 2 this was required to serialize dataclasses.dataclass instances. default False.")
        self.__parser.add_argument("--serialize-numpy", action="store_true", default=False,
                                   help="Serialize numpy.ndarray instances. default False.")
        self.__parser.add_argument("--serialize-uuid", action="store_true", default=False,
                                   help="This is deprecated and has no effect in version 3. In version 2 this was required to serialize uuid.UUID instances.  default False.")
        self.__parser.add_argument("--sort-keys", action="store_true", default=False,
                                   help="""Serialize keys in sorted order. The default is to serialize in an unspecified order. This is equivalent to in the standard library.dictsort_keys=True
This can be used to ensure the order is deterministic for hashing or tests. It has a substantial performance penalty and is not recommended in general.default False.""")
        self.__parser.add_argument("--strict-integer", action="store_true", default=False,
                                   help="Enforce 53-bit limit on integers. The limit is otherwise 64 bits, the same as the Python standard library. default False.")
        self.__parser.add_argument("--utc-z", action="store_true", default=False,
                                   help="Serialize a UTC timezone on instances as instead of .datetime.datetimeZ+00:00. default False.")
        self.__parser.set_defaults(func=self.__to_config)

    @staticmethod
    def __to_config(args):
        _set_value(JsonConfig, args)


class SerializeConfigParser(BaseArgParse):

    def __init__(self, action: _SubParsersAction):
        self.__parser = action.add_parser("serializeconfig", usage="serializeconfig --[autoname|camel|...]",
                                          description="serialize module global config")

    def parser(self):
        self.__parser.add_argument("--autoname", action="store_true", default=False,
                                   help="If the name of the json field is not specified and autoname is True, an attempt will be made to name the json field name with the attribute name, after a name is specified, autoname and camel do not take effect. default False.")
        self.__parser.add_argument("--camel", action="store_true", default=False,
                                   help="The recommended attribute format for python is snake, and this option will use camel, autoname is True will camel take effect. default False.")
        self.__parser.set_defaults(func=self.__to_config)

    @staticmethod
    def __to_config(args):
        _set_value(SerializeConfig, args)


def init():
    try:
        __SimpleboxArgParse().parser()
    except SystemExit:
        pass
