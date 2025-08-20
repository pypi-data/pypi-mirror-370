#!/usr/bin/env python
# -*- coding:utf-8 -*-
import itertools
from _ast import Call, Attribute
from ast import NodeVisitor, parse
from collections import defaultdict
from inspect import getsource

__all__ = []


def parser_private_attr_name(clz: type, origin_name: str) -> str:
    prefix = clz.__name__
    if not prefix.startswith("_"):
        prefix = f"_{prefix}"
    return origin_name.replace(prefix, "")


def rm_underline_start_end(string: str) -> str:
    new = itertools.dropwhile(lambda value: value == "_", string)
    new = itertools.dropwhile(lambda value: value == "_", list(new)[::-1])
    return "".join(list(new)[::-1]) or string


class AstTools:

    def __init__(self, target):
        self.__target = target
        self.__decorators = defaultdict(list)

    def __visit_hock(self, node):
        for n in node.decorator_list:
            if isinstance(n, Call):
                name = n.func.attr if isinstance(n.func, Attribute) else n.func.id
            else:
                name = n.attr if isinstance(n, Attribute) else n.id
            self.__decorators[node.name].append(name)

    def get_decorator_of_function_by_name(self, name) -> list:
        node_iter = NodeVisitor()
        node_iter.visit_FunctionDef = self.__visit_hock
        node_iter.visit_Await = self.__visit_hock
        node_iter.generic_visit(parse(getsource(self.__target)))
        return self.__decorators.get(name)

    def get_decorator_of_class_by_name(self, name) -> list:
        node_iter = NodeVisitor()
        node_iter.visit_ClassDef = self.__visit_hock
        node_iter.generic_visit(parse(getsource(self.__target)))
        return self.__decorators.get(name)
