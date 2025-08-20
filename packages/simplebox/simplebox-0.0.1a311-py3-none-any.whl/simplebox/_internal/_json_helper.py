#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Callable
from typing import Optional, Any, Union

import orjson

from ._serialization import _serializer
from ..collections import ArrayList
from ..config.json import JsonConfig
from ..config.serialize import SerializeConfig
from ..maps import Dictionary


def _build_option(option, orjson_option):
    if option is None:
        return orjson_option
    return option | orjson_option


def _inner_dumps(obj, *, default: Optional[Callable[[Any], Any]] = None, newline: bool = None, indent2: bool = None,
                 naive_utc: bool = None, non_str_keys: bool = None, omit_microseconds: bool = None,
                 passthrough_dataclass: bool = None, passthrough_datetime: bool = None,
                 passthrough_subclass: bool = None, serialize_dataclass: bool = None,
                 serialize_numpy: bool = None, serialize_uuid: bool = None, sort_keys: bool = None,
                 strict_integer: bool = None, utc_z: bool = None) -> bytes:
    """
    Serialize ``obj`` to a JSON formatted ``str``.
    :params ensure_ascii: If ``ensure_ascii`` is false, then the strings written to ``fp`` can
    contain non-ASCII characters if they appear in strings contained in
    ``obj``. Otherwise, all such characters are escaped in JSON strings.
    """
    option = None
    if newline is True or JsonConfig.newline:
        option = _build_option(option, orjson.OPT_APPEND_NEWLINE)
    if indent2 is True or JsonConfig.indent2:
        option = _build_option(option, orjson.OPT_INDENT_2)
    if naive_utc is True or JsonConfig.naive_utc:
        option = _build_option(option, orjson.OPT_NAIVE_UTC)
    if non_str_keys is True or JsonConfig.non_str_keys:
        option = _build_option(option, orjson.OPT_NON_STR_KEYS)
    if omit_microseconds is True or JsonConfig.omit_microseconds:
        option = _build_option(option, orjson.OPT_OMIT_MICROSECONDS)
    if passthrough_dataclass is True or JsonConfig.passthrough_dataclass:
        option = _build_option(option, orjson.OPT_PASSTHROUGH_DATACLASS)
    if passthrough_datetime is True or JsonConfig.passthrough_datetime:
        option = _build_option(option, orjson.OPT_PASSTHROUGH_DATETIME)
    if passthrough_subclass is True or JsonConfig.passthrough_subclass:
        option = _build_option(option, orjson.OPT_PASSTHROUGH_SUBCLASS)
    if serialize_dataclass is True or JsonConfig.serialize_dataclass:
        option = _build_option(option, orjson.OPT_SERIALIZE_DATACLASS)
    if serialize_numpy is True or JsonConfig.serialize_numpy:
        option = _build_option(option, orjson.OPT_SERIALIZE_NUMPY)
    if serialize_uuid is True or JsonConfig.serialize_uuid:
        option = _build_option(option, orjson.OPT_SERIALIZE_UUID)
    if sort_keys is True or JsonConfig.sort_keys:
        option = _build_option(option, orjson.OPT_SORT_KEYS)
    if strict_integer is True or JsonConfig.strict_integer:
        option = _build_option(option, orjson.OPT_STRICT_INTEGER)
    if utc_z is True or JsonConfig.utc_z:
        option = _build_option(option, orjson.OPT_UTC_Z)
    return orjson.dumps(_serializer(obj, SerializeConfig.camel), default=default or JsonConfig.default, option=option)


def _inner_loads(s: Union[bytes, bytearray, memoryview, str]) -> Any:
    """
    Deserialize ``s`` (a ``str``, ``bytes`` or ``bytearray`` instance
    containing a JSON document) to a Python object.
    """
    obj = orjson.loads(s)
    if isinstance(obj, dict):
        return Dictionary(obj)
    elif isinstance(obj, list):
        return ArrayList(obj)
    else:
        return obj
