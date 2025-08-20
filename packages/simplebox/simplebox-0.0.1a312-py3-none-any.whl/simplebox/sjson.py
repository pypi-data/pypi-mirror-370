#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import Any, IO, Union

from ._internal._json_helper import _inner_dumps, _inner_loads

"""
A simple json tool.
"""


def dump(obj, fp: IO[bytes or str], *, encoding="UTF-8", default=None, newline: bool = None, indent2: bool = None,
         naive_utc: bool = None, non_str_keys: bool = None, omit_microseconds: bool = None,
         passthrough_dataclass: bool = None, passthrough_datetime: bool = None, passthrough_subclass: bool = None,
         serialize_dataclass: bool = None, serialize_numpy: bool = None, serialize_uuid: bool = None,
         sort_keys: bool = None, strict_integer: bool = None, utc_z: bool = None) -> None:
    """Serialize ``obj`` as a JSON formatted stream to ``fp`` (a
    ``.write()``-supporting file-like object).
    :param obj: python object.
                This is usually a dict or list, but it can also be an object that inherits from the Serializable class.
    :param fp: open("file", "wb").
    :param default: To serialize a subclass or arbitrary types, specify as a callable that returns a supported type.
                    may be a function, lambda, or callable class instance.
                    To specify that a type was not handled by , raise an exception such as TypeError.
    :param encoding: bytes to str decode coding.
    :param newline: Append to the output. This is a convenience and optimization for the pattern of
                    objects is immutable and this pattern copies the original contents.\ndumps(...) + '\n'bytes.
    :param indent2: Pretty-print output with an indent of two spaces.
                    This is equivalent to in the standard library.
                    Pretty printing is slower and the output larger. orjson is the fastest compared library at pretty
                    printing and has much less of a slowdown to pretty print than the standard library does.
                    This option is compatible with all other options.indent=2.
    :param naive_utc: Serialize objects without a as UTC.
                    This has no effect on objects that have set.datetime.datetime tzinfo.
    :param non_str_keys: Serialize keys of type other than . This allows keys to be one of , , , , , , , , , and.
                        For comparison, the standard library serializes , , , or by default.
                        orjson benchmarks as being faster at serializing non- keys than other libraries.
                        This option is slower for keys than the default. dict,str,int,float,bool,None,datetime.datetime,
                        datetime.date,datetime.time,enum.Enum,uuid.UUID.
    :param omit_microseconds: Do not serialize the field on and instances.microsecond datetime.datetime datetime.time.
    :param passthrough_dataclass: Passthrough dataclasses.dataclass instances to default. This allows customizing their output but is much slower.
    :param passthrough_datetime: Passthrough dataclasses.dataclass instances to default. This allows customizing their output but is much slower.
    :param passthrough_subclass: Passthrough subclasses of builtin types to default.
    :param serialize_dataclass: This is deprecated and has no effect in version 3. In version 2 this was required to serialize dataclasses.dataclass instances.
    :param serialize_numpy: Serialize numpy.ndarray instances.
    :param serialize_uuid: This is deprecated and has no effect in version 3. In version 2 this was required to serialize uuid.UUID instances.
    :param sort_keys: Serialize keys in sorted order. The default is to serialize in an unspecified order. This is equivalent to in the standard library.dictsort_keys=True
                    This can be used to ensure the order is deterministic for hashing or tests. It has a substantial performance penalty and is not recommended in general.
    :param strict_integer: Enforce 53-bit limit on integers. The limit is otherwise 64 bits, the same as the Python standard library.
    :param utc_z: Serialize a UTC timezone on instances as instead of .datetime.datetimeZ+00:00

    """
    data = _inner_dumps(obj, default=default, newline=newline, indent2=indent2, naive_utc=naive_utc,
                        non_str_keys=non_str_keys, omit_microseconds=omit_microseconds,
                        passthrough_dataclass=passthrough_dataclass, passthrough_datetime=passthrough_datetime,
                        passthrough_subclass=passthrough_subclass, serialize_dataclass=serialize_dataclass,
                        serialize_numpy=serialize_numpy, serialize_uuid=serialize_uuid, sort_keys=sort_keys,
                        strict_integer=strict_integer, utc_z=utc_z)
    # noinspection PyBroadException
    try:
        fp.write(data)
    except BaseException:
        fp.write(data.decode(encoding=encoding))


def dumps(obj, *, default=None, encoding="UTF-8", newline: bool = None, indent2: bool = None, naive_utc: bool = None,
          non_str_keys: bool = None, omit_microseconds: bool = None, passthrough_dataclass: bool = None,
          passthrough_datetime: bool = None, passthrough_subclass: bool = None, serialize_dataclass: bool = None,
          serialize_numpy: bool = None, serialize_uuid: bool = None, sort_keys: bool = None,
          strict_integer: bool = None, utc_z: bool = None) -> str:
    """
    Serialize ``obj`` to a JSON formatted ``str``.
    :param obj: python object.
                This is usually a dict or list, but it can also be an object that inherits from the Serializable class.
    :param default: To serialize a subclass or arbitrary types, specify as a callable that returns a supported type.
                    may be a function, lambda, or callable class instance.
                    To specify that a type was not handled by , raise an exception such as TypeError.
    :param encoding: bytes to str decode coding.
    :param newline: Append to the output. This is a convenience and optimization for the pattern of
                    objects is immutable and this pattern copies the original contents.\ndumps(...) + '\n'bytes.
    :param indent2: Pretty-print output with an indent of two spaces.
                    This is equivalent to in the standard library.
                    Pretty printing is slower and the output larger. orjson is the fastest compared library at pretty
                    printing and has much less of a slowdown to pretty print than the standard library does.
                    This option is compatible with all other options.indent=2.
    :param naive_utc: Serialize objects without a as UTC.
                    This has no effect on objects that have set.datetime.datetime tzinfo.
    :param non_str_keys: Serialize keys of type other than . This allows keys to be one of , , , , , , , , , and.
                        For comparison, the standard library serializes , , , or by default.
                        orjson benchmarks as being faster at serializing non- keys than other libraries.
                        This option is slower for keys than the default. dict,str,int,float,bool,None,datetime.datetime,
                        datetime.date,datetime.time,enum.Enum,uuid.UUID.
    :param omit_microseconds: Do not serialize the field on and instances.microsecond datetime.datetime datetime.time.
    :param passthrough_dataclass: Passthrough dataclasses.dataclass instances to default. This allows customizing their output but is much slower.
    :param passthrough_datetime: Passthrough dataclasses.dataclass instances to default. This allows customizing their output but is much slower.
    :param passthrough_subclass: Passthrough subclasses of builtin types to default.
    :param serialize_dataclass: This is deprecated and has no effect in version 3. In version 2 this was required to serialize dataclasses.dataclass instances.
    :param serialize_numpy: Serialize numpy.ndarray instances.
    :param serialize_uuid: This is deprecated and has no effect in version 3. In version 2 this was required to serialize uuid.UUID instances.
    :param sort_keys: Serialize keys in sorted order. The default is to serialize in an unspecified order. This is equivalent to in the standard library.dictsort_keys=True
                    This can be used to ensure the order is deterministic for hashing or tests. It has a substantial performance penalty and is not recommended in general.
    :param strict_integer: Enforce 53-bit limit on integers. The limit is otherwise 64 bits, the same as the Python standard library.
    :param utc_z: Serialize a UTC timezone on instances as instead of .datetime.datetimeZ+00:00

    """
    return _inner_dumps(obj, default=default, newline=newline, indent2=indent2, naive_utc=naive_utc,
                        non_str_keys=non_str_keys, omit_microseconds=omit_microseconds,
                        passthrough_dataclass=passthrough_dataclass, passthrough_datetime=passthrough_datetime,
                        passthrough_subclass=passthrough_subclass, serialize_dataclass=serialize_dataclass,
                        serialize_numpy=serialize_numpy, serialize_uuid=serialize_uuid, sort_keys=sort_keys,
                        strict_integer=strict_integer, utc_z=utc_z).decode(encoding=encoding)


def load(fp: IO[str or bytes]) -> Any or dict or list:
    """
    Deserialize ``fp`` (a ``.read()``-supporting file-like object containing
    a JSON document) to a Python object.
    """

    return _inner_loads(fp.read())


def loads(s: Union[bytes, bytearray, memoryview, str]) -> Any:
    """
    Deserialize ``s`` (a ``str``, ``bytes`` or ``bytearray`` instance
    containing a JSON document) to a Python object.
    """
    return _inner_loads(s)
