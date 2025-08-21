from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from .constant import Regions
from ..setting import DEFAULT_CYBOZU_SUBDOMAIN, DEFAULT_CYBOZU_USERNAME, DEFAULT_CYBOZU_PASSWORD, \
    DEFAULT_OTP_SECRET, DEFAULT_CYBOZU_REGION, DEFAULT_APP_TOKENS


@dataclass
class AccessData:
    subdomain: str = DEFAULT_CYBOZU_SUBDOMAIN
    username: str = DEFAULT_CYBOZU_USERNAME
    password: str = DEFAULT_CYBOZU_PASSWORD
    is_dev: bool = False
    otp_secret: str = DEFAULT_OTP_SECRET
    region: Regions = Regions.from_str(DEFAULT_CYBOZU_REGION)
    app_tokens: dict[int, str] = field(default_factory=lambda: DEFAULT_APP_TOKENS.copy())

    @property
    def has_auth(self) -> bool:
        return len(self.username) > 0 and len(self.password) > 0

    @property
    def host(self) -> str:
        host: str = f"{self.subdomain}.cybozu"
        if self.is_dev:
            host = host + "-dev"
        if self.region == Regions.JP:
            host = host + ".com"
        elif self.region == Regions.CN:
            host = host + ".cn"
        else:
            raise NotImplementedError(f"Region {self.region} is not implemented.")
        return host


@dataclass
class CybozuDotComUrl(metaclass=ABCMeta):
    subdomain: str
    is_dev: bool

    @property
    def path(self) -> str:
        return ""

    @property
    @abstractmethod
    def _product(self) -> str:
        raise NotImplementedError()

    @property
    def fragment(self) -> str:
        return ""

    @property
    def params(self) -> dict[str, str]:
        return {}

    def fqdn(self, is_secure: bool = False) -> str:
        fqdn: str = f"{self.subdomain}"
        if is_secure:
            fqdn = fqdn + ".s"
        fqdn = fqdn + ".cybozu"
        if self.is_dev:
            fqdn = fqdn + "-dev"
        fqdn = fqdn + ".com"
        return fqdn

    def url(self, is_secure: bool = False, params: dict[str, str] | None = None) -> str:
        url_: str = f"https://{self.fqdn(is_secure)}/{self._product}/{self.path}"
        if self.fragment:
            url_ += "#" + self.fragment
        params_: dict[str, str] = params if params else {}
        params_.update(self.params)
        if params_:
            url_ += "?" + "&".join([f"{k}={v}" for k, v in params_.items()])
        return url_

    def __str__(self) -> str:
        return self.url()


@dataclass
class Notification:
    notify_at: datetime
    user_code: str
    text: str
    has_mention: bool
    subdomain: str
    is_dev: bool

    @property
    @abstractmethod
    def url(self) -> CybozuDotComUrl:
        raise NotImplementedError()


@dataclass(order=True)
class Comment(metaclass=ABCMeta):
    id: int = field(compare=False)
    text: str = field(compare=False)
    commented_at: datetime = field(compare=True)
    like_count: int = field(compare=False)
    like_codes: set[str] = field(compare=False)
    creator_code: str = field(compare=False)
    mention_codes: set[str] = field(compare=False)
    mention_org_codes: set[str] = field(compare=False)
    mention_group_codes: set[str] = field(compare=False)
    subdomain: str = field(compare=False)
    is_dev: bool = field(compare=False)

    @property
    @abstractmethod
    def url(self) -> CybozuDotComUrl:
        raise NotImplementedError()
