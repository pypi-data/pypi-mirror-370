from __future__ import annotations

from dataclasses import dataclass

from ...cybozu.dto import CybozuDotComUrl


@dataclass
class GaroonUrl(CybozuDotComUrl):
    @property
    def _product(self) -> str:
        return "g"


@dataclass
class GaroonEventUrl(GaroonUrl):
    event_id: int

    @property
    def path(self) -> str:
        return "schedule/view.csp"

    @property
    def params(self) -> dict[str, str]:
        return {"event": str(self.event_id)}


@dataclass
class GaroonSearchResultUrl(GaroonUrl):
    def __init__(self, subdomain: str, is_dev: bool, path: str):
        super().__init__(subdomain, is_dev)
        self._path: str = path.removeprefix(f"/{self._product}/")

    @property
    def path(self) -> str:
        return self._path


@dataclass
class GaroonNotificationUrl(GaroonUrl):
    def __init__(self, subdomain: str, is_dev: bool, path: str, params: dict[str, str]):
        super().__init__(subdomain, is_dev)
        self._path: str = path
        self._params: dict[str, str] = params

    @property
    def path(self) -> str:
        return self._path

    @property
    def params(self) -> dict[str, str]:
        return self._params
