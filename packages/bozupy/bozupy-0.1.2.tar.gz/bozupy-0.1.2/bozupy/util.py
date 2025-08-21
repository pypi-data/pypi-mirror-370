import logging
import os
import re
from datetime import datetime, timedelta, time, date
from typing import Pattern
from urllib.parse import ParseResult, urlparse

import requests
from lxml import html

_KINTONE_DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"
_KINTONE_DATETIME_FORMAT_JST: str = "%Y-%m-%dT%H:%M:%S+09:00"
_KINTONE_DATETIME_UTC_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"
_KINTONE_DATE_FORMAT: str = "%Y-%m-%d"
_KINTONE_TIME_FORMAT: str = "%H:%M"
_GAROON_DATE_FORMAT: str = "%Y年%m月%d"
_GAROON_TIME_FORMAT: str = "%H:%M"
_GAROON_JST_DATE_FORMAT: str = "%Y-%m-%dT00:00:00+09:00"
_GAROON_JST_DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S+09:00"

_DATETIME_FORMAT_LIST: list[str] = [
    "%Y/%m/%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    _GAROON_JST_DATE_FORMAT,
    _GAROON_JST_DATETIME_FORMAT
]
_DATE_FORMAT_LIST: list[str] = [
    "%Y/%m/%d",
    "%Y-%m-%d",
    "%Y年%m月%d日"
]
_TIME_FORMAT_LIST: list[str] = [
    "%H:%M:%S",
    "%H:%M"
]
_LINK_PATTERN: Pattern = re.compile(r"(https?://\S+)")
_URL_PATTERN: Pattern = re.compile(r"https?://[\w/:%#$&?()~.=+-]+")


def find_refs(text: str) -> set[str]:
    links: set[str] = set([])
    for link_str in _LINK_PATTERN.findall(text):
        schema_count: int = 0
        for scheme in ["https://", "http://"]:
            schema_count += link_str.count(scheme)
        if schema_count == 0:
            continue
        elif schema_count == 1:
            links.add(link_str)
            continue
        https_link_list: list[str] = link_str.split("https://")
        for https_link_ in https_link_list:
            if not https_link_:
                continue
            https_link: str = "https://" + https_link_
            for link in https_link.split("http://"):
                if not link:
                    continue
                if link.startswith("https://"):
                    links.add(link)
                else:
                    links.add("http://" + link)
    return links


def kintone_str_to_datetime(datetime_str: str) -> datetime:
    try:
        d: datetime = datetime.strptime(datetime_str, _KINTONE_DATETIME_FORMAT).replace(microsecond=0)
    except ValueError:
        d = datetime.strptime(datetime_str, _KINTONE_DATETIME_UTC_FORMAT).replace(microsecond=0)
    return d + timedelta(hours=9)  # JST


def datetime_to_kintone_utc_str(datetime_: datetime) -> str:
    datetime_str: str = datetime_.strftime(_KINTONE_DATETIME_UTC_FORMAT)
    if datetime_str.endswith("000Z"):
        # 3桁がほしいがstrftimeでの指定の仕方がわからないので手動で追加
        return datetime_str[:-4] + "Z"
    return datetime_str


def garoon_str_to_datetime(datetime_str: str) -> datetime:
    date_str: str = datetime_str.split("日")[0]
    time_str: str = datetime_str.split(" ")[1]
    date_: date = datetime.strptime(date_str, _GAROON_DATE_FORMAT).date()
    time_: time = datetime.strptime(time_str, _GAROON_TIME_FORMAT).time()
    return datetime(year=date_.year, month=date_.month, day=date_.day, hour=time_.hour, minute=time_.minute)


def datetime_to_garoon_jst_str(datetime_: datetime) -> str:
    if datetime_.tzinfo is not None:
        raise NotImplementedError("timezone is not implemented yet...")
    return datetime_.strftime(_GAROON_JST_DATETIME_FORMAT)


def date_to_garoon_jst_str(day: date) -> str:
    return day.strftime(_GAROON_JST_DATE_FORMAT)


def kintone_str_to_date(datetime_str: str) -> date:
    return kintone_str_to_datetime(datetime_str).date()


def date_to_kintone_str(day: date) -> str:
    return day.strftime(_KINTONE_DATE_FORMAT)


def time_to_kintone_str(time_: time) -> str:
    return time_.strftime(_KINTONE_TIME_FORMAT)


def datetime_to_kintone_str(datetime_: datetime) -> str:
    if datetime_.tzinfo is None:
        return datetime_.strftime(_KINTONE_DATETIME_FORMAT_JST)
    offset: timedelta | None = datetime_.tzinfo.utcoffset(datetime_)
    if offset is None:
        return datetime_.strftime(_KINTONE_DATETIME_FORMAT_JST)
    return (datetime_.replace(tzinfo=None) - offset).strftime(_KINTONE_DATETIME_FORMAT)


def kintone_date_str_to_date(date_str: str) -> date:
    return datetime.strptime(date_str, _KINTONE_DATE_FORMAT).date()


def datetime_to_str(datetime_: datetime) -> str:
    return datetime_.strftime(_DATETIME_FORMAT_LIST[0])


def str_to_datetime(datetime_str: str) -> datetime:
    e: Exception | None = None
    for format_ in _DATETIME_FORMAT_LIST:
        try:
            return datetime.strptime(datetime_str, format_)
        except ValueError as e1:
            e = e1
            continue
    for format_ in _DATE_FORMAT_LIST:
        try:
            return datetime.strptime(datetime_str, format_).replace(hour=0, minute=0, second=0, microsecond=0)
        except ValueError as e1:
            e = e1
            continue
    if e is not None:
        raise e
    raise RuntimeError("Failed to parse datetime")


def str_to_date(datetime_str: str) -> date:
    try:
        return str_to_datetime(datetime_str).date()
    except ValueError:
        return datetime.strptime(datetime_str, _KINTONE_DATE_FORMAT).date()


def str_to_time(time_str: str) -> time:
    e: Exception | None = None
    for format_ in _TIME_FORMAT_LIST:
        try:
            return datetime.strptime(time_str, format_).time()
        except ValueError as e1:
            e = e1
            continue
    if e is not None:
        raise e
    raise RuntimeError("Failed to parse time")


def date_to_str(day: date) -> str:
    return day.strftime(_KINTONE_DATE_FORMAT)


def html_to_text(html_str: str) -> str:
    if not html_str:
        return ""
    try:
        return str(html.fromstring(html_str).text_content())
    except ValueError:
        return str(html.fromstring(html_str.encode()).text_content())
    except Exception as ignored:
        logging.warning("Failed to parse html", exc_info=ignored)
        return ""


def dom_to_links(dom: html.HtmlElement, host: str) -> set[str]:
    links: set[str] = set([])
    for a_elm in dom.xpath(".//a"):
        if "data-mention-id" in a_elm.attrib or "data-group-mention-id" in a_elm.attrib or "data-org-mention-id" in a_elm.attrib:
            continue
        link: str | None = a_elm.get("href", None)
        if link is None:
            continue
        if link.startswith("/"):
            # パスの場合
            link = f"https://{host}{link}"
        links.add(link)
    return links


def input_text(is_one_line: bool = False) -> str:
    lines: list[str] = []
    while True:
        input_line = input()
        if input_line:
            lines.append(input_line.strip())
            if is_one_line:
                break
        elif is_one_line:
            continue
        else:
            break
    return '\n'.join(lines)


def debug_response_print(response: requests.Response) -> None:
    if os.environ.get("TEST", "") == "1":
        return
    log_message: str = "\n".join([
        "##request",
        str(response.request.url),
        str(response.request.headers),
        str(response.request.body),
        "",
        "##response",
        str(response.status_code),
        str(response.headers),
        str(response.text)
    ])
    if response.status_code >= 400:
        logging.warning(log_message)
    else:
        logging.debug(log_message)


def str_to_url_parse_result(url_str: str) -> tuple[ParseResult | None, str, bool]:
    if _URL_PATTERN.match(url_str) is None:
        return None, "", False
    url: ParseResult = urlparse(url_str)
    if url.hostname is None or (not url.hostname.endswith(".cybozu.com") and not url.hostname.endswith(".cybozu-dev.com")):
        return None, "", False
    is_dev: bool = False
    if url.hostname.endswith(".cybozu-dev.com"):
        is_dev = True
    subdomain: str = url.hostname.split(".")[0]
    return url, subdomain, is_dev


def str_to_url_params(param_str: str) -> dict[str, str]:
    params: dict[str, str] = {}
    for kv in param_str.split("&"):
        if "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        params[k] = v
    return params


def get_str_optional(d: dict, key: str) -> str | None:
    if key in d and d[key]:
        return str(d[key])
    return None


def get_datetime_optional(d: dict, key: str) -> datetime | None:
    if key in d and d[key]:
        return str_to_datetime(str(d[key]))
    return None


def get_date_optional(d: dict, key: str) -> date | None:
    if key in d and d[key]:
        return str_to_date(str(d[key]))
    return None


def get_int_optional(d: dict, key: str) -> int | None:
    if key in d and d[key]:
        return int(d[key])
    return None


def get_float_optional(d: dict, key: str) -> float | None:
    if key in d and d[key]:
        return float(d[key])
    return None


def json_get_optional(json_: dict[str, dict[str, str]], key1: str, key2: str = "value") -> str | None:
    if key1 in json_:
        if json_[key1] is None:
            return None
        return json_[key1].get(key2, None)
    return None
