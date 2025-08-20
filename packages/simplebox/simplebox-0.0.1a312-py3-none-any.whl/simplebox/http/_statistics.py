#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from urllib.parse import urlparse

from openpyxl.workbook import Workbook

__all__ = []


class UrlMeta:
    """
    url metadata
    """

    def __init__(self, url, method):
        self.__url = urlparse(url)
        self.__host = f"{self.__url.scheme}://{self.__url.netloc}"
        if self.__host == "://":
            self.__host = ""
        self.__netloc = self.__url.netloc
        self.__protocol = self.__url.scheme
        self.__port = self.__url.port or ""
        self.__path = self.__url.path
        self.__method = method
        self.__count: int = 1
        self.__dict = {"host": self.__host, "protocol": self.__protocol, "port": self.__port, "method": self.__method,
                       "api": self.__path, "count": self.__count}

    @property
    def protocol(self):
        return self.__protocol

    @property
    def host(self):
        return self.__host

    @property
    def path(self):
        return self.__path

    @property
    def port(self):
        return self.__port

    @property
    def method(self):
        """
        http method.
        :return:
        """
        return self.__method

    @property
    def count(self) -> int:
        """
        request send count.
        """
        return self.__count

    def __eq__(self, other: 'UrlMeta'):
        result = self.__method == other.__method and self.__protocol == other.__protocol \
                 and self.__netloc == other.__netloc and self.__port == other.__port \
                 and self.__path == other.__path
        if result is True:
            self.__count += 1
        self.__dict['count'] = self.__count
        return result

    def __hash__(self):
        return hash(f"{self.__method}:{self.__protocol}{self.__netloc}{self.__port}{self.__path}")

    def __str__(self):
        return str(self.__dict)

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:

        return self.__dict


class HostView:
    """
    url path statistics are performed in the host dimension
    like
    """

    def __init__(self, host):
        self.__host = host
        self.__paths: set[str] = set()
        self.__urls: set[UrlMeta] = set()

    @property
    def paths(self) -> list[str]:
        return list(self.__paths)

    @property
    def urls(self) -> list[UrlMeta]:
        return list(self.__urls)

    @property
    def host(self) -> str:
        return self.__host

    def add(self, *paths: UrlMeta):
        for p in paths:
            if p.host == self.__host:
                self.__paths.add(p.path)
                self.__urls.add(p)

    def path_numbers(self) -> int:
        return len(self.__paths)

    def __str__(self):
        return str({self.__host: {"paths": self.__paths, "urlMeta": self.__urls}})

    def __repr__(self):
        return self.__str__()


class StatsUrl:
    """
    statistics the URLs that have been sent.
    get_url_stats return a dict like {'host2': StatsUrlHostView, 'host2': StatsUrlHostView}
    """

    def __init__(self):
        self.__urls_stats: dict[str, HostView] = {}

    def __str__(self):
        return str(self.__urls_stats)

    def __repr__(self):
        return self.__str__()

    def add(self, *reqs: tuple[str, str]):
        for url, method in reqs:
            meta = UrlMeta(url, method)
            if meta.host not in self.__urls_stats:
                self.__urls_stats[meta.host] = HostView(meta.host)
            self.__urls_stats[meta.host].add(meta)

    @property
    def urls_stats(self) -> dict[str, HostView]:
        return self.__urls_stats

    def get_url_stats_by_host(self, host) -> HostView:
        return self.__urls_stats.get(host)


def aggregation(context) -> dict[str, dict[str, list[HostView]]]:
    """
    Aggregate all REST request data in context
    :param context: rest context.
    :return: {"do": info, "done": info},
            'do' is the api info for wrapper assembly,
            'done' is the api info for requested.
    """
    stats_do_urls: dict[str, list[HostView]] = {}
    stats_done_urls: dict[str, list[HostView]] = {}
    wrappers = []
    rests = []
    for bean in context.beans.values():
        wrappers.extend([wrapper.api_stats_do for wrapper in bean.wrappers.values()])
        rests.append(bean.rest.api_stats_done)

    for wrapper in wrappers:
        for host, view in wrapper.urls_stats.items():
            if host not in stats_do_urls:
                stats_do_urls[host] = [view]
            else:
                stats_do_urls[host].append(view)

    for rest in rests:
        for host, view in rest.urls_stats.items():
            if host not in stats_do_urls:
                stats_done_urls[host] = [view]
            else:
                stats_done_urls[host].append(view)

    return {"do": stats_do_urls, "done": stats_done_urls}


def export(context, file_name, file_type="json"):
    """
    export host and apis in context rests.
    :param context: rest context.
    :param file_name: export file name or path.
    :param file_type: export type. support json and xlsx. default type is json.
    :return:
    If you count the interfaces assembled by the wrapper, you may see duplicate interfaces because there is no host
    information at this time, so you cannot distinguish whether the same interface belongs to a different service.
    """

    def out_json(data, path):
        """
        format:
{
    "do": {
        "": [
            {
                "host": "",
                "protocol": "",
                "port": "",
                "method": "GET",
                "api": "/world",
                "count": 1
            },
            {
                "host": "",
                "protocol": "",
                "port": "",
                "method": "POST",
                "api": "/hello",
                "count": 1
            },
        ]
    },
    "done": {
        "http://localhost:8080": [
            {
                "host": "http://localhost:8080",
                "protocol": "http",
                "port": 8080,
                "method": "POST",
                "api": "/hello1",
                "count": 1
            },
            {
                "host": "http://localhost:8080",
                "protocol": "http",
                "port": 8080,
                "method": "GET",
                "api": "/hello",
                "count": 2
            }
        ]
    }
}
        """
        with open(path, "wb") as f:
            f.write(json.dumps(data, indent=4).encode("utf-8"))

    class Excel:

        def __init__(self, path):
            self.__wb = Workbook()
            self.__wb.remove(self.__wb.active)
            self.__path = path

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.__wb.save(str(self.__path))

        def new_sheet(self, name) -> 'Sheet':
            return Sheet(self.__wb.create_sheet(name))

    class Sheet:
        __xlsx_head = {"A": "host", "B": "protocol", "C": "port", "D": "method", "E": "api", "F": "count"}

        def __init__(self, sheet):
            self.__sheet = sheet
            self.__sheet.append(list(self.__xlsx_head.values()))
            for k in self.__xlsx_head.keys():
                attr_name = f"_{self.__class__.__name__}__col_{k.lower()}_max_dimensions"
                setattr(self, attr_name, 0)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.__set_column_dimensions()

        def __cal(self, **kwargs):
            for k, v in self.__xlsx_head.items():
                if v in kwargs:
                    attr_name = f"_{self.__class__.__name__}__col_{k.lower()}_max_dimensions"
                    if (v_len := len(str(kwargs.get(v)))) > getattr(self, attr_name):
                        setattr(self, attr_name, v_len)

        def __set_column_dimensions(self):
            for k in self.__xlsx_head.keys():
                fidle_name = f"_{self.__class__.__name__}__col_{k.lower()}_max_dimensions"
                self.__sheet.column_dimensions[k].width = int(getattr(self, fidle_name) + 4)

        def add(self, **kwargs):
            self.__cal(**kwargs)
            self.__sheet.append(list(kwargs.values()))

    def out_excel(data, path):
        with Excel(path) as excel:
            for stage, stage_data in data.items():
                with excel.new_sheet(stage) as sheet:
                    for host, meta in stage_data.items():
                        for view in meta:
                            sheet.add(**view)

    def reintegration():
        stats_urls: dict[str, dict[str, list[HostView]]] = aggregation(context)
        new_stats_data = {}
        for stage, stage_meta in stats_urls.items():
            new_stage_meta = {}
            for host, views in stage_meta.items():
                http_metas = []
                for view in views:
                    http_metas.extend([meta.to_dict() for meta in view.urls])
                new_stage_meta[host] = http_metas
            new_stats_data[stage] = new_stage_meta
        return new_stats_data

    if isinstance(file_type, str) and file_type.lower() not in ['json', "xlsx"]:
        raise TypeError(f"not support file type: {file_type}")
    info = reintegration()

    if file_type == "json":
        out_json(info, file_name)
    elif file_type == "xlsx":
        out_excel(info, file_name)
    return info
