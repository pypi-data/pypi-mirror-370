from dataclasses import dataclass

from ..constant import OperationTypes
from ..url.dto import GaroonNotificationUrl
from ...cybozu.dto import Notification
from ...util import str_to_url_params


@dataclass
class GaroonNotification(Notification):
    module: str
    creator_id: int
    operation_type: OperationTypes
    body: str
    is_read: bool
    link: str

    @property
    def url(self) -> GaroonNotificationUrl:
        path: str = self.link[self.link.index("/g/") + len("/g/"):]
        params: dict[str, str] = {}
        if "?" in path:
            params = str_to_url_params(path[path.index("?") + 1:])
            path = path[:path.index("?")]
        return GaroonNotificationUrl(
            subdomain=self.subdomain,
            is_dev=self.is_dev,
            path=path,
            params=params
        )

    @property
    def is_garoon_notify(self) -> bool:
        return self.module.startswith("grn.")
