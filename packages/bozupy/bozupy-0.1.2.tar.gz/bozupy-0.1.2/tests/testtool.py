import json
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from enum import Enum
from inspect import stack
from pathlib import Path
from typing import Any, Pattern

import requests
import responses
import yaml
from lxml import html
from responses import Response, add
from responses. matchers import header_matcher, query_param_matcher, json_params_matcher

from bozupy import AccessData

DUMMY_ACCESS_DATA: AccessData = AccessData(
    subdomain="test",
    username="username",
    password="password",
    app_tokens={1: "1", 2: "2"}
)


_TEST_RESOURCE_DIR = Path(__file__).parent / "resources"


def _get_resource_file(caller_filepath: str, filename: str, additional_path: str | None) -> Path:
    path: Path = Path(caller_filepath)
    items: list[str] = []
    while path.stem != "tests":
        items.append(path.stem.removeprefix("test_"))
        path = path.parent
    items.reverse()
    resource_dir: Path = _TEST_RESOURCE_DIR / Path(*items)
    if additional_path:
        resource_file: Path = resource_dir / additional_path / filename
    else:
        resource_file = resource_dir / filename
    if not resource_file.exists():
        raise FileNotFoundError(f"Resource file not found: {resource_file}")
    return resource_file


def load(filename: str, path: str | None = None) -> dict:
    resource_file: Path = _get_resource_file(stack()[1].filename, filename, path)
    match resource_file.suffix:
        case ".json":
            with resource_file.open(mode="r", encoding="utf-8") as f:
                return json.load(f)
        case ".yaml" | ".yml":
            with resource_file.open(mode="r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        case _:
            raise ValueError(f"Unsupported file type: {resource_file}")


def load_str(filename: str, path: str | None = None) -> str:
    resource_file: Path = _get_resource_file(stack()[1].filename, filename, path)
    with resource_file.open(mode="r", encoding="utf-8") as f:
        return f.read()


def load_dom(filename: str, path: str | None = None) -> html.HtmlElement:
    resource_file: Path = _get_resource_file(stack()[1].filename, filename, path)
    match resource_file.suffix:
        case ".html":
            with resource_file.open(mode="r", encoding="utf-8") as f:
                return html.fromstring(f.read())
        case _:
            raise ValueError(f"Unsupported file type: {resource_file}")


@contextmanager
def not_raises():
    try:
        yield
    except Exception as error:
        raise AssertionError(f"An unexpected exception {error} raised.")


def header_contains(headers: set[str]):
    def match(request: requests.Request):
        request_headers: dict = request.headers or {}
        valid: bool = (headers & set(request_headers.keys())) == headers
        if not valid:
            return False, f"Headers do not contains: {headers - set(request_headers.keys())}",
        return valid, ""
    return match


class _Match(metaclass=ABCMeta):
    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError()


class _AnyMatch(_Match):
    def __eq__(self, other: Any) -> bool:
        return True


any_match: _AnyMatch = _AnyMatch()


class AuthMode(Enum):
    PASSWORD = "PASSWORD"
    API_TOKEN = "API_TOKEN"
    REQUEST_TOKEN = "REQUEST_TOKEN"
    COOKIE = "COOKIE"


def set_mock_response(
        method: str,
        path: str,
        res_status: int = 200,
        res_json: dict | list | None = None,
        res_body: str | None = None,
        req_headers: dict[str, str | Pattern] | set[str] | None = None,
        req_json: dict[str, dict | list | str | int | float | _Match | None] | set[str] | None = None,
        req_params: dict[str, str | int | float | _Match] | set[str] | None = None,
        strict: bool = False,
        auth: AuthMode | None = None) -> None:
    # noinspection PyProtectedMember
    if responses.mock._patcher is None or not responses.mock._patcher.is_local:
        raise ValueError("@responses.activate decollator is not called.")
    if res_json is not None and res_body is not None:
        raise ValueError("Either res_json or res_body should be specified.")
    elif res_json is None and res_body is None and method.upper() != "GET":
        raise ValueError("Either res_json or res_body should be specified.")
    elif req_json is not None and req_params is not None:
        raise ValueError("Either req_json or req_params should be specified.")
    elif req_json is not None and method.upper() not in ["POST", "PUT", "PATCH", "DELETE"]:
        raise ValueError("req_json is specified but method is not POST, PUT, DELETE, or PATCH.")
    elif req_params is not None and method.upper() not in ["GET", "DELETE"]:
        raise ValueError("req_params is specified but method is not GET or DELETE.")
    matchers: list = []
    if auth:
        match auth:
            case AuthMode.PASSWORD:
                matchers.append(header_contains({"X-Cybozu-Authorization"}))
            case AuthMode.API_TOKEN:
                matchers.append(header_contains({"X-Cybozu-API-Token"}))
            case AuthMode.REQUEST_TOKEN:
                matchers.append(json_params_matcher({"__REQUEST_TOKEN__": any_match}, strict_match=False))
            case AuthMode.COOKIE:
                # TODO: ライブラリが自動でつけるCookieは確認する方法がなさそう？
                pass
            case _:
                raise ValueError(f"Unsupported auth mode: {auth}")
    if req_headers:
        if isinstance(req_headers, set):
            matchers.append(header_contains(req_headers))
        else:
            matchers.append(header_matcher(req_headers))
    if req_json:
        if isinstance(req_json, set):
            matchers.append(json_params_matcher({k: any_match for k in req_json}, strict_match=strict))
        else:
            matchers.append(json_params_matcher(req_json, strict_match=strict))
    elif req_params:
        if isinstance(req_params, set):
            matchers.append(query_param_matcher({k: any_match for k in req_params}, strict_match=strict))
        else:
            matchers.append(query_param_matcher(req_params, strict_match=strict))
    if res_json is not None:
        res: Response = Response(
            method=method.upper(),
            url=f"https://{DUMMY_ACCESS_DATA.host}{path}",
            status=res_status,
            json=res_json,
            content_type="application/json; charset=utf-8",
            match=matchers
        )
    elif res_body is not None:
        res = Response(
            method=method.upper(),
            url=f"https://{DUMMY_ACCESS_DATA.host}{path}",
            status=res_status,
            body=res_body,
            content_type="plain/text",
            match=matchers
        )
    else:
        res = Response(
            method=method.upper(),
            url=f"https://{DUMMY_ACCESS_DATA.host}{path}",
            status=res_status,
            match=matchers
        )
    add(res)
