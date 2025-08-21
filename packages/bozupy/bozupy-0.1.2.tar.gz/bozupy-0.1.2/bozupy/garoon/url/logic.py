from .dto import GaroonUrl, GaroonEventUrl
from ...util import str_to_url_parse_result, str_to_url_params


def parse_garoon_url(url_str: str) -> GaroonUrl | None:
    url, subdomain, is_dev = str_to_url_parse_result(url_str)
    if url is None:
        return None
    path: str = url.path
    if not path.startswith("/g/"):
        return None
    elif path.startswith("/g/schedule/view.csp"):
        params: dict[str, str] = str_to_url_params(url.query)
        if "event" not in params:
            return None
        try:
            event_id: int = int(params["event"])
        except ValueError:
            return None
        return GaroonEventUrl(subdomain=subdomain, event_id=event_id, is_dev=is_dev)
    return None
