from datetime import timedelta

from .dto import KintoneRecordComment
from ...util import str_to_datetime


# 公式API用
def to_record_comment(comment_json: dict, app_id: int, record_id: int, subdomain: str, is_dev: bool) -> KintoneRecordComment:
    mention_codes: set[str] = set([])
    mention_org_codes: set[str] = set([])
    mention_group_codes: set[str] = set([])
    for mention_json in comment_json["mentions"]:
        match mention_json["type"]:
            case "USER":
                mention_codes.add(mention_json["code"])
            case "ORGANIZATION":
                mention_org_codes.add(mention_json["code"])
            case "GROUP":
                mention_group_codes.add(mention_json["code"])
            case _:
                continue
    return KintoneRecordComment(
        id=int(comment_json["id"]),
        text=str(comment_json["text"]),
        commented_at=str_to_datetime(comment_json["createdAt"]) + timedelta(hours=9),
        like_count=0,  # 今の公式APIではいいね！数は取得できないので0にしておく
        like_codes=set([]),
        creator_code=comment_json["creator"]["code"],
        mention_codes=mention_codes,
        mention_org_codes=mention_org_codes,
        mention_group_codes=mention_group_codes,
        subdomain=subdomain,
        is_dev=is_dev,
        app_id=app_id,
        record_id=record_id
    )
