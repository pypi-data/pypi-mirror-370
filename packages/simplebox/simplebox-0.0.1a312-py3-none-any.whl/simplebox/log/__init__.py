#!/usr/bin/env python
# -*- coding:utf-8 -*-
_TRACE_ID_KEY = "trace_id_map_key"
_TRACE_DEFAULT_PATTERN = "%TRACEID%"

from ._factory import LoggerFactory

__all__ = [LoggerFactory]
