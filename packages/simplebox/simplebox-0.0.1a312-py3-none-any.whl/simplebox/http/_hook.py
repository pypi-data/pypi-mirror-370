#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import Callable, Optional, Any, Union

__all__ = []

from simplebox.utils.objects import ObjectsUtils


class HookSendBefore:
    """
    run at the http send request before
    """

    def __init__(self, run: Callable[[Optional[dict]], Optional[dict]], order: int = 0):
        self.__run: Callable[[Optional[dict]], Optional[dict]] = run
        self.__order: int = order

    def __eq__(self, other):
        return self.__run == other.__run and self.__order == other.__order

    def __hash__(self):
        return hash(self.__run) + self.__order

    def __str__(self):
        return f"{self.__run.__name__}:{self.__order}"

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self.__order < other.__order

    @property
    def order(self) -> int:
        return self.__order

    def run(self, kwargs) -> Optional[dict]:
        return self.__run(kwargs)


class HookSendAfter:
    """
    run at the http send request before
    """

    def __init__(self, run: Callable[[Any], Any], order: int = 0):
        """
        :param run: it is a callback function, http request finish will call,
                    and the response of the request will be injected into the callback function.
        :param order: the order in which they are executed.
        """
        self.__run: Callable[[Any], Any] = run
        self.__order: int = order

    def __eq__(self, other):
        return self.__run == other.__run and self.__order == other.__order

    def __hash__(self):
        return hash(self.__run) + self.__order

    def __str__(self):
        return f"{self.__run.__name__}:{self.__order}"

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self.__order < other.__order

    @property
    def order(self) -> int:
        return self.__order

    def run(self, response) -> Any:
        return self.__run(response)


class Hooks:
    """
    hook manager
    """

    def __init__(self, hook_before_list=None, hook_after_list=None):
        ObjectsUtils.check_type(hook_before_list, list, tuple, type(None))
        ObjectsUtils.check_type(hook_after_list, list, tuple, type(None))
        self.__hook_before_list = [] if hook_before_list is None else list(hook_before_list)
        self.__hook_after_list = [] if hook_after_list is None else list(hook_after_list)

    def __str__(self):
        return f"{self.__class__.__name__}=(before={self.__hook_before_list}, after={self.__hook_after_list})"

    def __repr__(self):
        return self.__str__()

    def add(self, *hooks: Union[HookSendBefore, HookSendAfter, list[Union[HookSendBefore, HookSendAfter], ...],
    tuple[Union[HookSendBefore, HookSendAfter], ...]]) -> 'Hooks':
        insert_before = False
        insert_after = False
        for hook in hooks:
            if isinstance(hook, HookSendBefore):
                insert_before = True
                self.__hook_before_list.append(hook)
            elif isinstance(hook, HookSendAfter):
                insert_after = True
                self.__hook_after_list.append(hook)
            elif isinstance(hook, (list, tuple)):
                self.add(hook)
        if insert_before:
            self.__hook_before_list.sort()
        if insert_after:
            self.__hook_after_list.sort()
        return self

    def add_hook_before(self, *hooks: Union[HookSendBefore, list[HookSendBefore, ...], tuple[HookSendBefore, ...]]) \
            -> 'Hooks':
        self.add(*hooks)
        return self

    def add_hook_after(self, *hooks: Union[HookSendAfter, list[HookSendAfter, ...], tuple[HookSendAfter, ...]]) \
            -> 'Hooks':
        self.add(*hooks)
        return self

    @property
    def before_hooks(self) -> list[HookSendBefore]:
        return self.__hook_before_list[:]

    @property
    def after_hooks(self) -> list[HookSendAfter]:
        return self.__hook_after_list[:]

    @staticmethod
    def copy(other: 'Hooks'):
        ObjectsUtils.check_type(other, Hooks)
        return Hooks(other.before_hooks, other.after_hooks)

    def merge(self, other: 'Hooks'):
        self.before_hooks.extend(other.before_hooks)
        self.after_hooks.extend(other.after_hooks)


def _filter_hook(hooks, excepted_type: type) -> list:
    hooks_list = []
    if isinstance(hooks, excepted_type):
        hooks_list.append(hooks)
    elif isinstance(hooks, list):
        hooks_list.extend((hook for hook in hooks if isinstance(hook, excepted_type)))
    return hooks_list
