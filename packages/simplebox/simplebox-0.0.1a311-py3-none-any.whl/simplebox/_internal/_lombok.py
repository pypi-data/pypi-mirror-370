#!/usr/bin/env python
# -*- coding:utf-8 -*-

def _build_setter(name: str, attr_name: str):
    func_code = f"""
def __set_{name}(self, value):
    self.{attr_name} = value
"""
    return func_code.strip()


def _build_getter(name: str, attr_name: str):
    func_code = f"""
def __get_{name}(self):
    return self.{attr_name}
"""
    return func_code.strip()


def _build_deleter(name: str, attr_name: str):
    func_code = f"""
def __del_{name}(self):
    del self.{attr_name}
"""
    return func_code.strip()


def _build_property(name, fget=None, fset=None, fdel=None):
    property_code = "cls.{name} = property(fget={fget}, fset={fset}, fdel={fdel})"
    return property_code.format(name=name, fget=fget, fset=fset, fdel=fdel)


def _parser_attr_name(clz: type) -> list[tuple[str, str]]:
    attrs_names = []
    prefix = f"_{clz.__name__}"
    for key in clz.__dict__.keys():
        k = key.strip()
        if (k.startswith("__") and k.endswith("__")) or k == "_":
            continue
        attrs_names.append((k.strip(prefix).strip("_"), k))
    return attrs_names


def _generator(cls, instance, getter: bool = True, setter: bool = True, deleter: bool = True):
    attrs_names = _parser_attr_name(cls)
    codes = []
    for name, origin_name in attrs_names:
        code = ""
        fget, fset, fdel = None, None, None
        if getter:
            if hasattr(instance, name) or hasattr(cls, name):
                continue
            code += _build_getter(name, origin_name) + "\n\n"
            fget = f"__get_{name}"
        if setter:
            if hasattr(instance, name) or hasattr(cls, name):
                continue
            code += _build_setter(name, origin_name) + "\n\n"
            fset = f"__set_{name}"
        if deleter:
            if hasattr(instance, name) or hasattr(cls, name):
                continue
            code += _build_deleter(name, origin_name) + "\n\n"
            fdel = f"__del_{name}"
        code += _build_property(name=name, fget=fget, fset=fset, fdel=fdel) + "\n\n"
        codes.append(code)
    exec("\n".join(codes))
