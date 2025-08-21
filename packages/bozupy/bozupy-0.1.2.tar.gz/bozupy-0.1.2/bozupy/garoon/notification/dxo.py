from .dto import GaroonNotification
from ..constant import OperationTypes
from ...util import str_to_datetime


# https://cybozu.dev/ja/garoon/docs/rest-api/notification/get-notification-items/

def to_garoon_notification(notification_json: dict, subdomain: str, is_dev: bool) -> GaroonNotification:
    return GaroonNotification(
        notify_at=str_to_datetime(notification_json["createdAt"]),
        user_code=str(notification_json["creator"]["code"]),
        text=str(notification_json["title"]),
        link=str(notification_json["url"]),
        has_mention=False,
        module=str(notification_json["moduleId"]),
        creator_id=int(notification_json["creator"]["id"]),
        operation_type=OperationTypes.from_str(notification_json["operation"]),
        body=str(notification_json["body"]),
        is_read=bool(notification_json["isRead"]),
        subdomain=subdomain,
        is_dev=is_dev
    )
