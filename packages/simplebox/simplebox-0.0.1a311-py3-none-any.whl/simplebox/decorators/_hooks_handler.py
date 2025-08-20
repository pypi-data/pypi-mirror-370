#!/usr/bin/env python
# -*- coding:utf-8 -*-
import inspect
from inspect import Parameter
from collections.abc import Iterable, Callable

__all__ = []


def _parser(func):
    if isinstance(func, staticmethod):
        origin = func.__func__
        sign = inspect.signature(origin)
        return origin, origin.__qualname__.split(".")[0], sign, 1
    elif isinstance(func, classmethod):
        origin = func.__func__
        sign = inspect.signature(origin)
        return origin, origin.__qualname__.split(".")[0], sign, 2
    elif inspect.ismethod(func):
        sign = inspect.signature(func)
        return func, func.__func__.__qualname__.split(".")[0], sign, 3
    else:
        if not isinstance(func, Callable):
            raise TypeError(f"{func} could not callable.")
        sign = inspect.signature(func)
        full_name = func.__qualname__
        if "." in full_name:
            return func, full_name.split(".")[0], sign, 0
        else:
            return func, None, sign, 0


def _build(func, args, kwargs, hooks):
    func_call, func_target, func_signature, func_type = _parser(func)
    func_arguments = func_signature.bind(*args, **kwargs)
    func_arguments.apply_defaults()
    if hooks is None:
        hooks = []
    else:
        if not isinstance(hooks, Iterable):
            hooks = [hooks]

    hook_map = {}
    for hook_ in hooks:
        hook_call, hook_target, hook_signature, hook_type = _parser(hook_)
        hook_parameters: dict[str, Parameter] = hook_signature.parameters
        hook_args = []
        hook_kwargs = {}
        arguments = dict(func_arguments.arguments)
        join = False
        for p in hook_parameters.values():
            if p.name in arguments:
                kind = p.kind
                if kind == p.POSITIONAL_ONLY or kind == p.POSITIONAL_OR_KEYWORD:
                    hook_args.append(arguments.pop(p.name))
                elif kind == p.VAR_POSITIONAL:
                    hook_args.extend(arguments.pop(p.name))
                elif kind == p.VAR_KEYWORD:
                    hook_kwargs.update(arguments.pop(p.name))
                else:
                    hook_kwargs[p.name] = arguments.pop(p.name)
            else:
                if hook_type == 2 and not join:
                    obj = args[0]
                    if hook_target == func_target:
                        if inspect.isclass(object):
                            hook_args.insert(0, obj)
                        else:
                            hook_args.insert(0, obj.__class__)
                        join = True
        if hook_type in [1, 2]:
            hook_map[hook_call] = (hook_args, hook_kwargs)
        else:
            hook_map[hook_] = (hook_args, hook_kwargs)
    return hook_map


def _run(meta):
    for hook_, arguments in meta.items():
        args, kwargs = arguments
        hook_(*args, **kwargs)
