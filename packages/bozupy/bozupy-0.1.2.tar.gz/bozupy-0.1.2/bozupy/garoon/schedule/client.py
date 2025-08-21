import logging
from datetime import datetime, date

import requests

# 何故かこの０ファイルだけfrom .dxo import to_eventだとテストでモックできなくなるので回避策
from . import dxo
from .dto import GaroonEvent, Facility
from ...cybozu.dto import AccessData
from ...cybozu.util import get_headers, check_response
from ...util import datetime_to_garoon_jst_str, date_to_garoon_jst_str, garoon_str_to_datetime

_DEFAULT_LIMIT: int = 100


def get_event(event_id: int, access_data: AccessData | None = None) -> GaroonEvent:
    logging.info(f"Get Event: {event_id}")
    if access_data is None:
        access_data = AccessData()
    # https://cybozu.dev/ja/garoon/docs/rest-api/schedule/get-schedule-event/
    res: requests.Response = requests.get(
        f"https://{access_data.host}/g/api/v1/schedule/events/{event_id}",
        headers=get_headers(access_data=access_data)
    )
    check_response(res)
    return dxo.to_event(res.json())


def add_event(start: datetime, end: datetime, title: str, attendees: set[str], access_data: AccessData | None = None) -> int:
    logging.info(f"Add Event: {title}")
    if access_data is None:
        access_data = AccessData()
    res: requests.Response = requests.post(
        f"https://{access_data.host}/g/api/v1/schedule/events",
        headers=get_headers(access_data=access_data, has_body=True),
        json={
            "eventType": "REGULAR",
            "subject": title,
            "start": {
                "dateTime": datetime_to_garoon_jst_str(start),
                "timeZone": "Asia/Tokyo"
            },
            "end": {
                "dateTime": datetime_to_garoon_jst_str(end),
                "timeZone": "Asia/Tokyo"
            },
            "attendees": [
                {
                    "type": "USER",
                    "code": attendee
                } for attendee in attendees
            ]
        }
    )
    check_response(res)
    return int(res.json()["id"])


def update_event(event_id: int, start: datetime | None, end: datetime, title: str, attendees: set[str], access_data: AccessData | None = None) -> None:
    logging.info(f"Update Event: {event_id}: {title}")
    if access_data is None:
        access_data = AccessData()
    res: requests.Response = requests.patch(
        f"https://{access_data.host}/g/api/v1/schedule/events/{event_id}",
        headers=get_headers(access_data=access_data, has_body=True),
        json={
            "eventType": "REGULAR",
            "subject": title,
            "start": {
                "dateTime": datetime_to_garoon_jst_str(start) if start else None,
                "timeZone": "Asia/Tokyo"
            },
            "end": {
                "dateTime": datetime_to_garoon_jst_str(end),
                "timeZone": "Asia/Tokyo"
            },
            "attendees": [
                {
                    "type": "USER",
                    "code": attendee
                } for attendee in attendees
            ]
        }
    )
    check_response(res)
    return None


def search_events(access_data: AccessData | None = None, query: str | None = None, user_id: int | None = None, start: date | None = None, end: date | None = None) -> list[GaroonEvent]:
    logging.info("Search Events")
    if access_data is None:
        access_data = AccessData()
    params: dict = {
        "limit": str(_DEFAULT_LIMIT),
    }
    events: list[dict] = []
    while True:
        params["offset"] = len(events)
        if query:
            params["keyword"] = query
        if start:
            params["rangeStart"] = date_to_garoon_jst_str(start)
        if end:
            params["rangeEnd"] = date_to_garoon_jst_str(end)
        if user_id:
            params["targetType"] = "user"
            params["target"] = str(user_id)
        res: requests.Response = requests.get(
            f"https://{access_data.host}/g/api/v1/schedule/events",
            headers=get_headers(access_data=access_data),
            params=params
        )
        check_response(res)
        result: list[dict] = res.json().get("events", [])
        events.extend(result)
        if len(result) < _DEFAULT_LIMIT:
            break
    return [dxo.to_event(event) for event in events]


def get_available_times(user_codes: list[str], time_interval: int, start: datetime, end: datetime, access_data: AccessData | None = None) -> list[tuple[datetime, datetime]]:
    logging.info("Get Available Times")
    if access_data is None:
        access_data = AccessData()
    params: dict = {
        "timeRanges": {
            "start": datetime_to_garoon_jst_str(start),
            "end": datetime_to_garoon_jst_str(end)
        },
        "timeInterval": time_interval,
        "attendees": [
            {"type": "USER", "code": user_code} for user_code in user_codes
        ]
    }
    res: requests.Response = requests.post(
        f"https://{access_data.host}/g/api/v1/schedule/searchAvailableTimes",
        headers=get_headers(access_data=access_data, has_body=True),
        json=params
    )
    check_response(res)
    times_list: list[dict] = res.json().get("availableTimes", [])
    return [(garoon_str_to_datetime(json_["start"]), garoon_str_to_datetime(json_["end"])) for json_ in times_list]


def get_event_data_store(access_data: AccessData, event_id: int, name: str) -> dict:
    logging.info(f"Get Event Data Store: {event_id}: {name}")
    res: requests.Response = requests.get(
        f"https://{access_data.host}/g/api/v1/schedule/events/{event_id}/datastore/{name}",
        headers=get_headers(access_data=access_data)
    )
    check_response(res)
    return res.json()["value"]


def add_event_data_store(access_data: AccessData, event_id: int, name: str, data: dict[str, str | int | dict | list]) -> None:
    logging.info(f"Add Event Data Store: {event_id}: {name}")
    res: requests.Response = requests.post(
        f"https://{access_data.host}/g/api/v1/schedule/events/{event_id}/datastore/{name}",
        headers=get_headers(access_data=access_data, has_body=True),
        json={"value": data}
    )
    check_response(res)


def update_event_data_store(access_data: AccessData, event_id: int, name: str, data: dict[str, str | int | dict | list]) -> None:
    logging.info(f"Update Event Data Store: {event_id}: {name}")
    res: requests.Response = requests.put(
        f"https://{access_data.host}/g/api/v1/schedule/events/{event_id}/datastore/{name}",
        headers=get_headers(access_data=access_data, has_body=True),
        json={"value": data}
    )
    check_response(res)


def get_facilities(access_data: AccessData) -> list[Facility]:
    logging.info("Get Facilities")
    facilities: list[dict] = []
    params: dict = {
        "limit": str(_DEFAULT_LIMIT),
    }
    while True:
        params["offset"] = len(facilities)
        res: requests.Response = requests.get(
            f"https://{access_data.host}/g/api/v1/schedule/facilities",
            headers=get_headers(access_data=access_data),
            params=params
        )
        check_response(res)
        result: list[dict] = res.json().get("facilities", [])
        facilities.extend(result)
        if len(result) < _DEFAULT_LIMIT:
            break
    return [dxo.to_facility(facility) for facility in facilities]
