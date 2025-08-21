from datetime import date, datetime, timedelta, timezone, time

from lxml import html

import pytest

from bozupy import util as sut


@pytest.mark.parametrize(["input_", "expected"], [
    ["2023-01-01", date(2023, 1, 1)],
    ["2023-01-01T00:00:00Z", date(2023, 1, 1)],
    ["2023-01-01T00:00:00.000Z", date(2023, 1, 1)],
    ["2023年01月01日", date(2023, 1, 1)]
])
def test_str_to_date(input_: str, expected: date):
    actual: date = sut.str_to_date(input_)
    assert actual == expected


@pytest.mark.parametrize(["input_", "expected"], [
    ["00:00:00", time(0, 0, 0)],
    ["00:00", time(0, 0, 0)],
])
def test_str_to_time(input_: str, expected: time):
    actual: time = sut.str_to_time(input_)
    assert actual == expected


@pytest.mark.parametrize(["input_", "expected"], [
    [date(2023, 1, 1), "2023-01-01"]
])
def test_date_to_str(input_: date, expected: str):
    actual: str = sut.date_to_str(input_)
    assert actual == expected


@pytest.mark.parametrize(["input_", "expected"], [
    ["", ""],
    [None, ""],
    ["<div>test</div>", "test"],
    ["<div>test</div><div>test</div>", "testtest"],
    ["</test test", ""]
])
def test_html_to_text(input_: str, expected: str):
    actual: str = sut.html_to_text(input_)
    assert actual == expected


@pytest.mark.parametrize(["input_", "expected"], [
    ['<div><a href="https://host/1"></div>', {"https://host/1"}],
    ['<div><a href="https://host/1"><a href="https://host/2"></div>', {"https://host/1", "https://host/2"}],
    ['<div><a data-mention-id="1" href="https://host/1"><a href="https://host/2"></div>', {"https://host/2"}],
    ['<div><a data-group-mention-id="1" href="https://host/1"><a href="https://host/2"></div>', {"https://host/2"}],
    ['<div><a data-org-mention-id="1" href="https://host/1"><a href="https://host/2"></div>', {"https://host/2"}],
    ['<div><a /></div>', set([])],
    ['<div><a href="/1"></div>', {"https://host/1"}]
])
def test_dom_to_links(input_: str, expected: set[str]):
    actual: set[str] = sut.dom_to_links(html.fromstring(input_), "host")
    assert actual == expected


@pytest.mark.parametrize(["input_", "expected"], [
    [datetime(2024, 1, 1, 0, 0, 0), "2024-01-01T00:00:00+09:00"],
    [datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc), "2024-01-01T00:00:00Z"],
    [datetime(2024, 1, 1, 9, 0, 0, tzinfo=timezone(timedelta(hours=9))), "2024-01-01T00:00:00Z"]
])
def test_datetime_to_kintone_str(input_: datetime, expected: str):
    assert sut.datetime_to_kintone_str(input_) == expected


def test_find_refs() -> None:
    text: str = """
おはようございます。
以下確認お願いします。
https://www.google.com/1
これもhttps://www.google.com/2/ 確認お願いします。
https://www.google.com/3?hoge=1 確認お願いします。
https://www.google.com/4/%E3%81%8A%E9%A1%98%E3%81%84%E3%81%97%E3%81%BE%E3%81%99%E3%80%82
https://www.google.com/#/5/
https://www.google.com/#/6/https://www.google.com/#/7/
https://www.google.com/#/8/http://www.google.com/#/9/https://www.google.com/#/8/https://www.google.com/#/10/
"""
    actual: set[str] = sut.find_refs(text)
    assert actual == {
        "https://www.google.com/1",
        "https://www.google.com/2/",
        "https://www.google.com/3?hoge=1",
        "https://www.google.com/4/%E3%81%8A%E9%A1%98%E3%81%84%E3%81%97%E3%81%BE%E3%81%99%E3%80%82",
        "https://www.google.com/#/5/",
        "https://www.google.com/#/6/",
        "https://www.google.com/#/7/",
        "https://www.google.com/#/8/",
        "http://www.google.com/#/9/",
        "https://www.google.com/#/10/"
    }


@pytest.mark.parametrize(["input_", "expected", "expected_subdomain", "expected_is_dev"], [
    ["hoge", False, "", False],
    ["https://hoge.cybozu.com", True, "hoge", False],
    ["https://hoge.cybozu-dev.com", True, "hoge", True],
    ["https://hoge.cybozu.co.jp", False, "", False]
])
def test_str_to_url_parse_result(input_: str, expected: bool, expected_subdomain: str, expected_is_dev: bool):
    actual_url, actual_subdomain, actual_is_dev = sut.str_to_url_parse_result(input_)
    assert (actual_url is not None) is expected
    assert actual_subdomain == expected_subdomain
    assert actual_is_dev == expected_is_dev


@pytest.mark.parametrize(["input_", "expected"], [
    ["", {}],
    ["hoge", {}],
    ["hoge=fuga", {"hoge": "fuga"}],
    ["hoge=fuga&piyo=piyo", {"hoge": "fuga", "piyo": "piyo"}],
    ["hoge=fuga&piyo=piyo&", {"hoge": "fuga", "piyo": "piyo"}],
    ["hoge=fuga&piyo=piyo&fuga", {"hoge": "fuga", "piyo": "piyo"}]
])
def test_str_to_url_params(input_: str, expected: dict):
    assert sut.str_to_url_params(input_) == expected


@pytest.mark.parametrize(["input_", "expected"], [
    [{"hoge": "fuga"}, "fuga"],
    [{"hoge": ""}, None],
    [{"hoge": None}, None],
    [{"hoge": 1}, "1"],
    [{}, None]
])
def test_get_str_optional(input_: dict, expected: str | None):
    assert sut.get_str_optional(input_, "hoge") == expected


@pytest.mark.parametrize(["input_", "expected"], [
    [{"hoge": "2023-01-01"}, datetime(2023, 1, 1, 0, 0, 0)],
    [{"hoge": "2023-01-01T00:00:00Z"}, datetime(2023, 1, 1, 0, 0, 0)],
    [{"hoge": "2023-01-01T00:00:00.000Z"}, datetime(2023, 1, 1, 0, 0, 0)],
    [{"hoge": "2023年01月01日"}, datetime(2023, 1, 1, 0, 0, 0)],
    [{"hoge": ""}, None],
    [{"hoge": None}, None],
    [{}, None]
])
def test_get_datetime_optional(input_: dict, expected: datetime | None):
    assert sut.get_datetime_optional(input_, "hoge") == expected


@pytest.mark.parametrize(["input_", "expected"], [
    [{"hoge": "2023-01-01"}, date(2023, 1, 1)],
    [{"hoge": "2023-01-01T00:00:00Z"}, date(2023, 1, 1)],
    [{"hoge": "2023-01-01T00:00:00.000Z"}, date(2023, 1, 1)],
    [{"hoge": "2023年01月01日"}, date(2023, 1, 1)],
    [{"hoge": ""}, None],
    [{"hoge": None}, None],
    [{}, None]
])
def test_get_date_optional(input_: dict, expected: date | None):
    assert sut.get_date_optional(input_, "hoge") == expected


@pytest.mark.parametrize(["input_", "expected"], [
    [{"hoge": "1"}, 1],
    [{"hoge": ""}, None],
    [{"hoge": None}, None],
    [{}, None]
])
def test_get_int_optional(input_: dict, expected: int | None):
    assert sut.get_int_optional(input_, "hoge") == expected


@pytest.mark.parametrize(["input_", "expected"], [
    [{"hoge": "1.1"}, 1.1],
    [{"hoge": ""}, None],
    [{"hoge": None}, None],
    [{}, None]
])
def test_get_float_optional(input_: dict, expected: float | None):
    assert sut.get_float_optional(input_, "hoge") == expected


@pytest.mark.parametrize(["data", "key1", "key2", "expected"], [
    [{}, "key1", "key2", None],
    [{"key1": {}}, "key1", "key2", None],
    [{"key1": {"key2": "value"}}, "key1", "key2", "value"],
    [{"key1": None}, "key1", "key2", None],
])
def test_json_get_optional(data: dict[str, dict[str, str]], key1: str, key2: str, expected: str | None) -> None:
    assert sut.json_get_optional(data, key1, key2) == expected
