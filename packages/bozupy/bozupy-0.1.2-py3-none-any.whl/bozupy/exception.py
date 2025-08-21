from dataclasses import dataclass

import requests


@dataclass
class LoginRequired(requests.HTTPError):
    # 401
    response: requests.Response


@dataclass
class AccessForbidden(requests.HTTPError):
    # 403
    response: requests.Response


@dataclass
class RateLimitExceeded(requests.HTTPError):
    # 429
    response: requests.Response


@dataclass
class RequestNotSuccess(requests.HTTPError):
    # 520
    response: requests.Response | None
    json_: dict | None = None


@dataclass
class APIError(requests.HTTPError):
    # 520
    response: requests.Response


@dataclass
class NoJsonResponse(requests.HTTPError):
    response: requests.Response
