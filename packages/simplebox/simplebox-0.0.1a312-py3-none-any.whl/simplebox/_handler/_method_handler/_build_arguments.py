#!/usr/bin/env python
# -*- coding:utf-8 -*-
from inspect import signature

__all__ = []


def _arguments_to_parameters(func, args, kwargs):
    bounds = signature(func).bind(*args, **kwargs)
    bounds.apply_defaults()
    return dict(bounds.arguments)
