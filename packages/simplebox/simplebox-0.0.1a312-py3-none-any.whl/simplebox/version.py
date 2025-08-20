#!/usr/bin/env python
# -*- coding:utf-8 -*-
import platform
import re




class Version:
    """
    Compare semantic version numbers
>>> version_a = Version("3.10")
    >>> version_b = Version("3.10.0")
    >>> version_c = Version("3.10.6")
    >>> version_d = Version("3.10.6-alpha")
    >>> version_e = Version("3.10.6+build.1234")

    >>> str(version_a)
    '3.10.0'
    >>> str(version_b)
    '3.10.0'
    >>> str(version_c)
    '3.10.6'
    >>> str(version_d)
    '3.10.6-alpha'
    >>> str(version_e)
    '3.10.6+build.1234'

    >>> version_a == version_b
    True
    >>> version_a != version_c
    True
    >>> version_d < version_c
    True
    >>> version_c <= version_c
    True
    >>> version_d > version_c
    False
    >>> version_c >= version_c
    True
    """
    def __init__(self, version):
        match = re.match(
            r'^(\d+)\.(\d+)(?:\.(\d+))?(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.['
            r'0-9A-Za-z-]+)*))?',
            version)
        if not match:
            raise ValueError(f"Invalid version string: {version}")

        self.major = int(match.group(1))
        self.minor = int(match.group(2))
        self.patch = int(match.group(3) or 0)
        self.pre_release = match.group(4) or ''
        self.build_metadata = match.group(5) or ''

    def _compare(self, other):
        # Compare main parts (major, minor, patch)
        for a, b in zip((self.major, self.minor, self.patch), (other.major, other.minor, other.patch)):
            if a != b:
                return a - b

        # If main parts are equal, compare pre-release identifiers
        if bool(self.pre_release) != bool(other.pre_release):
            return -1 if self.pre_release else 1

        if self.pre_release and other.pre_release:
            for this, that in zip(self.pre_release.split('.'), other.pre_release.split('.')):
                if this.isdigit() and that.isdigit():
                    comparison = int(this) - int(that)
                else:
                    comparison = (this > that) - (this < that)
                if comparison:
                    return comparison

            # If one list is longer, the shorter one is considered smaller.
            return len(self.pre_release.split('.')) - len(other.pre_release.split('.'))

        return 0

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._compare(other) == 0

    def __ne__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._compare(other) != 0

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._compare(other) < 0

    def __le__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._compare(other) <= 0

    def __gt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._compare(other) > 0

    def __ge__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._compare(other) >= 0

    def __str__(self):
        version = f"{self.major}.{self.minor}"
        if self.patch > 0:
            version += f".{self.patch}"
        if self.pre_release:
            version += f"-{self.pre_release}"
        if self.build_metadata:
            version += f"+{self.build_metadata}"
        return version


def check_py_version_gt(version: str):
    """
    check current python version greater than version.

    # current python is 3.10.6
    >>>check_py_version_gt("3.11.1")
    False
    >>>check_py_version_gt("3.11")
    False
    >>>check_py_version_gt("3.10")
    True
    >>>check_py_version_gt("3.10.6")
    False
    >>>check_py_version_gt("3.10.7")
    False
    """
    return Version(platform.python_version()) > Version(version)


def check_py_version_ge(version: str):
    """
    check current python version greater than and equal version.

    # current python is 3.10.6
    >>>check_py_version_ge("3.11.1")
    False
    >>>check_py_version_ge("3.11")
    False
    >>>check_py_version_ge("3.10")
    True
    >>>check_py_version_ge("3.10.6")
    True
    >>>check_py_version_ge("3.10.7")
    False
    """
    return Version(platform.python_version()) >= Version(version)


def check_py_version_lt(version: str):
    """
    check current python version lesser than version.

    # current python is 3.10.6
    >>>check_py_version_lt("3.11.1")
    True
    >>>check_py_version_lt("3.11")
    True
    >>>check_py_version_lt("3.10")
    False
    >>>check_py_version_lt("3.10.6")
    False
    >>>check_py_version_lt("3.10.7")
    True
    """
    return Version(platform.python_version()) < Version(version)


def check_py_version_le(version: str):
    """
    check current python version lesser than and equal version.

    # current python is 3.10.6
    >>>check_py_version_le("3.11.1")
    True
    >>>check_py_version_le("3.11")
    True
    >>>check_py_version_le("3.10")
    False
    >>>check_py_version_le("3.10.6")
    True
    >>>check_py_version_le("3.10.7")
    True
    """
    return Version(platform.python_version()) <= Version(version)


def check_py_version_eq(version: str):
    """
    check current python version lesser than and equal version.

    # current python is 3.10.6
    >>>check_py_version_eq("3.11.1")
    False
    >>>check_py_version_eq("3.11")
    False
    >>>check_py_version_eq("3.10")
    False
    >>>check_py_version_eq("3.10.6")
    True
    >>>check_py_version_eq("3.10.7")
    False
    """
    return Version(platform.python_version()) == Version(version)


def check_py_version_ne(version: str):
    """
    check current python version lesser than and equal version.

    # current python is 3.10.6
    >>>check_py_version_ne("3.11.1")
    True
    >>>check_py_version_ne("3.11")
    True
    >>>check_py_version_ne("3.10")
    True
    >>>check_py_version_ne("3.10.6")
    False
    >>>check_py_version_ne("3.10.7")
    True
    """
    return Version(platform.python_version()) != Version(version)
