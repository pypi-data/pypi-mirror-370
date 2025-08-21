import logging
from typing import Iterator

import requests

from ...cybozu.dto import AccessData
from ...cybozu.util import get_headers, check_response
from .dxo import to_garoon_notification
from .dto import GaroonNotification


def get_notifications(access_data: AccessData | None = None, not_read_only: bool = True) -> Iterator[GaroonNotification]:
    logging.info("Get Notifications")
    if access_data is None:
        access_data = AccessData()
    params: dict[str, int] = {"limit": 100}
    offset: int = 0
    has_next: bool = True
    while has_next:
        if offset > 0:
            params["offset"] = offset
        res: requests.Response = requests.get(
            f"https://{access_data.host}/g/api/v1/notification/items",
            headers=get_headers(access_data=access_data),
            params=params
        )
        check_response(res)
        json_: dict = res.json()
        for ntf in json_["items"]:
            if not_read_only and ntf["isRead"]:
                continue
            yield to_garoon_notification(ntf, access_data.subdomain, access_data.is_dev)
        has_next = json_["hasNext"]
        offset += len(json_["items"])
