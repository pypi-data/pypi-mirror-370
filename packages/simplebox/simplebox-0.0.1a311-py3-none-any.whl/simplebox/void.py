#!/usr/bin/env python
# -*- coding:utf-8 -*-
from collections.abc import Iterable

from .classes import Final


class Void(metaclass=Final):
    """
    Represents an empty or useless object
    """

    def __str__(self):
        return ""

    def __repr__(self):
        return ""

    def __bytes__(self):
        return b''

    def __hash__(self):
        return 0

    def __next__(self):
        return None

    def __bool__(self):
        return False

    def __contains__(self, item):
        return False

    def __len__(self):
        return 0

    def __eq__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __ne__(self, other):
        return False

    def __getattr__(self, item):
        return self

    def __getattribute__(self, item):
        return self

    def __setattr__(self, key, value):
        pass

    def __delattr__(self, item):
        pass

    def __dir__(self) -> Iterable[str]:
        return []

    def __del__(self):
        pass

    def __add__(self, other):
        return 0

    def __sub__(self, other):
        return 0

    def __mul__(self, other):
        return 0

    def __truediv__(self, other):
        return 0

    def __floordiv__(self, other):
        return 0

    def __mod__(self, other):
        return 0

    def __divmod__(self, other):
        return 0

    def __pow__(self, power, modulo=None):
        return 0

    def __lshift__(self, other):
        return 0

    def __rshift__(self, other):
        return 0

    def __and__(self, other):
        return 0

    def __xor__(self, other):
        return 0

    def __or__(self, other):
        return 0

    def __radd__(self, other):
        return 0

    def __rsub__(self, other):
        return 0

    def __rmul__(self, other):
        return 0

    def __rdiv__(self, other):
        return 0

    def __rmod__(self, other):
        return 0

    def __rmatmul__(self, other):
        return 0

    def __rtruediv__(self, other):
        return 0

    def __rfloordiv__(self, other):
        return 0

    def __rdivmod__(self, other):
        return 0

    def __rpow__(self, other):
        return 0

    def __rlshift__(self, other):
        return 0

    def __rrshift__(self, other):
        return 0

    def __rand__(self, other):
        return 0

    def __rxor__(self, other):
        return 0

    def __ror__(self, other):
        return 0

    def __iadd__(self, other):
        raise NotImplementedError

    def __isub__(self, other):
        raise NotImplementedError

    def __imul__(self, other):
        raise NotImplementedError

    def __itruediv__(self, other):
        raise NotImplementedError

    def __ifloordiv__(self, other):
        raise NotImplementedError

    def __imod__(self, other):
        raise NotImplementedError

    def __ipow__(self, other):
        raise NotImplementedError

    def __ilshift__(self, other):
        raise NotImplementedError

    def __irshift__(self, other):
        raise NotImplementedError

    def __iand__(self, other):
        raise NotImplementedError

    def __ixor__(self, other):
        raise NotImplementedError

    def __ior__(self, other):
        raise NotImplementedError

    def __pos__(self):
        raise NotImplementedError

    def __neg__(self):
        raise NotImplementedError

    def __abs__(self):
        raise NotImplementedError

    def __invert__(self):
        raise NotImplementedError

    def __complex__(self):
        raise NotImplementedError

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __round__(self, n=None):
        return 0

    def __index__(self):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __getitem__(self, item):
        return self

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __iter__(self):
        raise StopIteration

    def __reversed__(self):
        raise NotImplementedError
