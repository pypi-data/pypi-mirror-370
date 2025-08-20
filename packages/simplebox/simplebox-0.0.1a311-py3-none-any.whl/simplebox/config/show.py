#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
temp show all config run as python command line
~: python -m simplebox.config.show
"""
from inspect import currentframe, getframeinfo
from pathlib import Path

stack = getframeinfo(currentframe().f_back)
if stack.function != "_run_code" and Path(stack.filename).name != "runpy.py":
    raise ImportError("not found module")
else:
    import os
    from ..config.log import LogConfig
    from ..config.rest import RestConfig
    from ..config.property import PropertyConfig
    from ..config.json import JsonConfig
    from ..config.serialize import SerializeConfig
    os.environ['SB_BANNER_OFF'] = 'False'
    LogConfig.off_banner = True
    LogConfig.off = True
    print(LogConfig)
    print(RestConfig)
    print(PropertyConfig)
    print(JsonConfig)
    print(SerializeConfig)
