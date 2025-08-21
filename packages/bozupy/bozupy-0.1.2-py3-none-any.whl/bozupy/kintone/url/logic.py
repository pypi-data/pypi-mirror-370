import re
from typing import Pattern, Match

from .dto import KintoneUrl, KintoneAppUrl, KintoneRecordCommentUrl, KintoneRecordUrl, KintoneSpaceUrl, \
    KintoneThreadUrl, KintoneThreadCommentUrl, KintoneThreadChildCommentUrl, KintonePeopleUrl, KintonePeopleCommentUrl, \
    KintonePeopleChildCommentUrl, KintoneMessageUrl, KintoneMessageCommentUrl
from ...util import str_to_url_parse_result, str_to_url_params

_APP_PATH_PATTERN: Pattern = re.compile(r"/k/(\d+)/?")
_RECORD_PATH_PATTERN: Pattern = re.compile(r"/k/(\d+)/show")


def parse_kintone_url(url_str: str) -> KintoneUrl | None:
    url, subdomain, is_dev = str_to_url_parse_result(url_str)
    if url is None:
        return None
    path: str = url.path
    app_match: Match[str] | None = _APP_PATH_PATTERN.match(path)
    if app_match is not None:
        # アプリ
        app_id: int = int(app_match.group(1))
        record_match: Match[str] | None = _RECORD_PATH_PATTERN.match(path)
        if record_match is None:
            return KintoneAppUrl(subdomain=subdomain, app_id=app_id, is_dev=is_dev)
        else:
            record_id: int | None = None
            record_comment_id: int | None = None
            params: dict[str, str] = str_to_url_params(url.fragment.strip("#"))
            if "record" in params:
                try:
                    record_id = int(params["record"])
                except ValueError:
                    return None
            if "comment" in params:
                try:
                    record_comment_id = int(params["comment"])
                except ValueError:
                    return None
            if record_id is None:
                # アプリ
                return KintoneAppUrl(subdomain=subdomain, app_id=app_id, is_dev=is_dev)
            else:
                if record_comment_id is not None:
                    # レコードコメント
                    return KintoneRecordCommentUrl(subdomain=subdomain, app_id=app_id, record_id=record_id, comment_id=record_comment_id, is_dev=is_dev)
                else:
                    # レコード
                    return KintoneRecordUrl(subdomain=subdomain, app_id=app_id, record_id=record_id, is_dev=is_dev)
    fragment: str = url.fragment
    if "?" in fragment:
        fragment = fragment.split("?", 1)[0]
    if fragment.endswith("/"):
        fragment = fragment[:-1]
    fragments: list[str] = fragment.split("/")
    if fragment.startswith("/space/"):
        try:
            space_id: int = int(fragments[2])
        except ValueError:
            return None
        match len(fragments):
            case 3:
                # スペース
                return KintoneSpaceUrl(subdomain=subdomain, space_id=space_id, is_dev=is_dev)
            case 5:
                # スレッド
                try:
                    thread_id: int = int(fragments[4])
                except ValueError:
                    return None
                return KintoneThreadUrl(subdomain=subdomain, space_id=space_id, thread_id=thread_id, is_dev=is_dev)
            case 6:
                # スレッドコメント(親)
                try:
                    thread_id = int(fragments[4])
                    comment_id: int = int(fragments[5])
                except ValueError:
                    return None
                return KintoneThreadCommentUrl(subdomain=subdomain, space_id=space_id, thread_id=thread_id, comment_id=comment_id, is_dev=is_dev)
            case 7:
                # スレッドコメント(子)
                try:
                    thread_id = int(fragments[4])
                    parent_id: int = int(fragments[5])
                    comment_id = int(fragments[6])
                except ValueError:
                    return None
                return KintoneThreadChildCommentUrl(subdomain=subdomain, space_id=space_id, thread_id=thread_id, parent_comment_id=parent_id, comment_id=comment_id, is_dev=is_dev)
            case _:
                return None
    elif fragment.startswith("/people/user/"):
        people_code: str = fragments[3]
        match len(fragments):
            case 4:
                # ピープル
                return KintonePeopleUrl(subdomain=subdomain, user_code=people_code, is_dev=is_dev)
            case 5:
                # ピープルコメント(親)
                try:
                    comment_id = int(fragments[4])
                except ValueError:
                    return None
                return KintonePeopleCommentUrl(subdomain=subdomain, user_code=people_code, comment_id=comment_id, is_dev=is_dev)
            case 6:
                # ピープルコメント(子)
                try:
                    parent_id = int(fragments[4])
                    comment_id = int(fragments[5])
                except ValueError:
                    return None
                return KintonePeopleChildCommentUrl(subdomain=subdomain, user_code=people_code, parent_comment_id=parent_id, comment_id=comment_id, is_dev=is_dev)
            case _:
                return None
    elif fragment.startswith("/message/"):
        try:
            id1: int = int(fragments[2].split(";")[0])
            id2: int = int(fragments[2].split(";")[1])
        except ValueError:
            return None
        if id2 < id1:
            id1, id2 = id2, id1
        match len(fragments):
            case 3:
                # メッセージ
                return KintoneMessageUrl(subdomain=subdomain, user_id1=id1, user_id2=id2, is_dev=is_dev)
            case 4:
                # メッセージコメント
                try:
                    comment_id = int(fragments[3])
                except ValueError:
                    return None
                return KintoneMessageCommentUrl(subdomain=subdomain, user_id1=id1, user_id2=id2, comment_id=comment_id, is_dev=is_dev)
            case _:
                return None
    return None
