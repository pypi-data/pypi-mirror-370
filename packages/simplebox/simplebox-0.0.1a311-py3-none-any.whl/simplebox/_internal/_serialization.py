#!/usr/bin/env python
# -*- coding:utf-8 -*-
import types
from types import GenericAlias
from typing import Generic, Any, final

from ..config.serialize import SerializeConfig
from ..exceptions import SerializeException, NotImplementedException
from ..generic import T
from ..utils.strings import StringUtils
from . import _tools


def __serializer_parser_iter(values, camel):
    l = []
    l_append = l.append
    for value in values:
        l_append(__serializer_parser(value, camel))
    return l


def __serializer_parser_dict(values, camel):
    d = {}
    for key, value in values.items():
        if camel:
            k = StringUtils.convert_to_camel(key).origin()
        else:
            k = key
        d[k] = __serializer_parser(value, camel)
    return d


def __serializer_parser(value, camel):
    if issubclass(type(value), (list, tuple, set)):
        return __serializer_parser_iter(value, camel)
    elif issubclass(type(value), dict):
        return __serializer_parser_dict(value, camel)
    elif isinstance(value, _Serializable):
        return value.serializer()
    return value


def _serializer(value, camel):
    return __serializer_parser(value, camel)


def __deserializer_parser_iter(clz, data, camel):
    l = []
    l_append = l.append
    for value in data:
        l_append(__deserializer_parser(clz, value, camel))
    return l


def __deserializer_parser_dict(clz, data, camel):
    d = {}
    for key, value in data.items():
        if camel:
            k = StringUtils.convert_to_camel(key).origin()
        else:
            k = key
        d[k] = __deserializer_parser(clz, value, camel)
    return d


def __deserializer_parser(clz, data, camel):
    if issubclass(type(data), (list, tuple, set)):
        return __deserializer_parser_iter(clz, data, camel)
    elif issubclass(type(data), dict):
        return __deserializer_parser_dict(clz, data, camel)
    elif isinstance(data, _Serializable):
        return clz().deserializer(data)
    return data


def _deserializer(clz, data, camel):
    return __deserializer_parser(clz, data, camel)


class _SerializeField:
    __params__ = ['name', 'autoname', 'camel', 'hooks', 'types']

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        instance.__attr_name__ = None
        __head = f"{_SerializeField.__name__}__"
        for param in _SerializeField.__params__:
            setattr(instance, f"{__head}{param}", kwargs.get(param, None))
        return instance

    def __set_name__(self, owner, name):
        self.__attr_name__ = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.__attr_name__)

    def __set__(self, instance, value):
        if instance is not None:
            self.__types_handler(instance, value)
            instance.__dict__[self.__attr_name__] = self.__hook_handler(instance, value)

    @final
    def __hook_handler(self, instance, value):
        hooks = self.__hooks
        if hooks is not None:
            if not isinstance(hooks, (list, tuple)):
                raise TypeError(f'{instance.__class__.__name__}.'
                                f'{_tools.parser_private_attr_name(instance.__class__, self.__attr_name__)} '
                                f'params "types" type error: Excepted type "tuple[Callable[[Any], tuple[bool, Any]]] '
                                f'or list[Callable[[Any], tuple[bool, Any]]]", got "{type(hooks).__name__}"')
            for hook in hooks:
                result, value = hook(value)
                if not result:
                    raise SerializeException(f"{instance.__class__.__name__}."
                                             f"{_tools.parser_private_attr_name(instance.__class__, self.__attr_name__)}"
                                             f" hook exec fail: hook result fail => '{result}', '{value}'.")
        return value

    @final
    def __types_handler(self, instance, value):
        if self.__types:
            types_ = self.__types[:]
        else:
            return
        if types_:
            if not isinstance(types_, (list, tuple)):
                raise TypeError(f'{instance.__class__.__name__}.'
                                f'{_tools.parser_private_attr_name(instance.__class__, self.__attr_name__)} '
                                f'params "types" type error: Excepted type "tuple[type]", got "{type(types).__name__}"')
            for t in types_:
                if isinstance(t, GenericAlias):
                    if isinstance(value, (list, tuple)):
                        for generic_type in t.__args__:
                            for v in value:
                                if not isinstance(v, generic_type):
                                    raise TypeError(f'{instance.__class__.__name__}.'
                                                    f'{_tools.parser_private_attr_name(instance.__class__, self.__attr_name__)}: '
                                                    f'Excepted type "{generic_type}", got "{type(value).__name__}"')
                    elif isinstance(value, dict):
                        generic_types = t.__args__
                        for k, v in value.items():
                            if not isinstance(k, generic_types[0]):
                                raise TypeError(f'{instance.__class__.__name__}.'
                                                f'{_tools.parser_private_attr_name(instance.__class__, self.__attr_name__)}: '
                                                f'Excepted type "{generic_types[0]}", got "{type(value).__name__}"')
                            if not isinstance(v, generic_types[1]):
                                raise TypeError(f'{instance.__class__.__name__}.'
                                                f'{_tools.parser_private_attr_name(instance.__class__, self.__attr_name__)}: '
                                                f'Excepted type "{generic_types[1]}", got "{type(value).__name__}"')
                else:
                    if not isinstance(value, t):
                        raise TypeError(f'{instance.__class__.__name__}.'
                                        f'{_tools.parser_private_attr_name(instance.__class__, self.__attr_name__)}: '
                                        f'Excepted type "{[type_.__name__ for type_ in types_]}", '
                                        f'got "{type(value).__name__}"')


class _Serializable(Generic[T]):
    __field_head = f"{_SerializeField.__name__}__"

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        head = f"_{cls.__name__}"
        instance.__head__ = head
        instance.__serialize_fields = dict(instance.__class__.__dict__)
        return instance

    @final
    def __get_field_attr(self, field: _SerializeField, attr_name):
        return getattr(field, f"{self.__field_head}{attr_name}", None)

    @property
    def autoname(self) -> bool:
        return False

    @property
    def camel(self) -> bool:
        return False

    @final
    def __serializer(self) -> dict[str, T]:
        d = {}
        index = 0
        for key, value in self.__dict__.items():
            if key not in self.__serialize_fields:
                continue
            v = self.__serialize_fields.get(key)
            if isinstance(v, _SerializeField):
                index += 1
                camel = self.__get_field_attr(v, "camel") or self.camel or SerializeConfig.camel
                name = self.__get_field_attr(v, "name")
                if not name:
                    if key.startswith(self.__head__):
                        name = key.replace(self.__head__, "")
                    else:
                        name = key
                    if self.__get_field_attr(v, "autoname") or self.autoname or SerializeConfig.autoname:
                        name = _tools.rm_underline_start_end(name)
                        if camel:
                            name = StringUtils.convert_to_camel(name).origin()
                if (name and (len(name) == 1 and name == "_")) or StringUtils.is_black(name):
                    continue
                d[name] = _serializer(value, camel)
        return d

    @final
    def serializer(self) -> dict[str, T] or Any:
        """
        For serialization operations, custom serialization methods are used first,
        and defaults are used if not implemented
        :return:
        """
        try:
            return self.custom_serializer()
        except (NotImplementedError, NotImplementedException):
            return self.__serializer()

    def custom_serializer(self):
        """
        A custom serialization interface is provided to the user, and if the interface is implemented,
        the serialization results of the interface are preferentially used。
        :return:
        """
        raise NotImplementedException("need implemented")

    @final
    def __deserializer(self, data: dict):

        index = 0
        for key, value in self.__dict__.items():
            if key not in self.__serialize_fields:
                continue
            v = self.__serialize_fields.get(key)
            if isinstance(v, _SerializeField):
                index += 1
                camel = self.__get_field_attr(v, "camel") or self.camel or SerializeConfig.camel
                name = self.__get_field_attr(v, "name")
                if not name:
                    if key.startswith(self.__head__):
                        name = key.replace(self.__head__, "")
                    else:
                        name = key
                    if self.__get_field_attr(v, "autoname") or self.autoname or SerializeConfig.autoname:
                        name = _tools.rm_underline_start_end(name)
                        if camel:
                            name = StringUtils.convert_to_camel(name).origin()
                if (name and (len(name) == 1 and name == "_")) or StringUtils.is_black(name):
                    continue
                types = self.__get_field_attr(v, "types")
                value_in_data = data[name]
                if types:
                    for t in types:
                        if isinstance(value_in_data, (list, tuple)):
                            l = []
                            if isinstance(t, GenericAlias):
                                for generic_type in t.__args__:
                                    for v in value_in_data:
                                        obj = generic_type()
                                        obj.deserializer(v)
                                        l.append(obj)
                            else:
                                for v in value_in_data:
                                    l.append(v)
                            self.__dict__[key] = l
                        elif isinstance(value_in_data, dict):
                            d = {}
                            if isinstance(t, GenericAlias):
                                generic_types = t.__args__
                                for dict_k, dict_v in value_in_data.items():
                                    if isinstance(dict_v, generic_types[1]):
                                        obj = generic_types[1]()
                                        obj.deserializer(v)
                                        d[dict_k] = obj
                            else:
                                d.update(value_in_data)
                            self.__dict__[key] = d
                        else:
                            self.__dict__[key] = _deserializer(v, data[name], camel)

                else:
                    self.__dict__[key] = _deserializer(v, data[name], camel)

    @final
    def deserializer(self, data: dict):
        """
        SerializeField types must set Class type
        :return:
        """
        try:
            return self.custom_deserializer(data)
        except (NotImplementedError, NotImplementedException):
            return self.__deserializer(data)

    def custom_deserializer(self, data: dict):
        """
        SerializeField types must set Class type
        """
        raise NotImplementedException("need implemented")


__all__ = [_Serializable, _SerializeField, _serializer]
