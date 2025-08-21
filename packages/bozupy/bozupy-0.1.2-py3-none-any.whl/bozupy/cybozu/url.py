from .dto import CybozuDotComUrl
from ..kintone.url import logic as kintone_logic
from ..garoon.url import logic as garoon_logic


def parse_url(url_str: str) -> CybozuDotComUrl | None:
    if "/k/" in url_str:
        return kintone_logic.parse_kintone_url(url_str)
    elif "/g/" in url_str:
        return garoon_logic.parse_garoon_url(url_str)
    return None
