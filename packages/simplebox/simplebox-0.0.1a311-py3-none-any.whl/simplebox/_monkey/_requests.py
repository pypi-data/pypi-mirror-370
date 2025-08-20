#!/usr/bin/env python
# -*- coding:utf-8 -*-
from requests import PreparedRequest, Response

from .._requests._models import _prepare_headers, _prepare_body, _resp_json

PreparedRequest.prepare_headers = _prepare_headers
PreparedRequest.prepare_body = _prepare_body
Response.json = _resp_json


