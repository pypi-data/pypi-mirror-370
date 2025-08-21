from .dto import GaroonEvent, Facility
from ..constant import EventTypes
from ...util import str_to_datetime


def to_event(event_json: dict) -> GaroonEvent:
    return GaroonEvent(
        id=int(event_json["id"]),
        subject=event_json["subject"],
        creator_code=event_json["creator"]["code"],
        event_type=EventTypes.from_str(event_json["eventType"]),
        start=str_to_datetime(event_json["start"]["dateTime"]),
        end=str_to_datetime(event_json["end"]["dateTime"]) if "end" in event_json and event_json["end"] else None,
        created_at=str_to_datetime(event_json["createdAt"]),
        attendee_codes=set([attendee["code"] for attendee in event_json.get("attendees", [])]),
        watcher_codes=set([watcher["code"] for watcher in event_json.get("watchers", [])]),
        facility_codes=set([facility["code"] for facility in event_json.get("facilities", [])]),
        note=event_json.get("note", None),
        label=event_json.get("label", None)
    )


def to_facility(facility_json: dict) -> Facility:
    return Facility(
        code=facility_json["code"],
        id=int(facility_json["id"]),
        name=facility_json["name"],
        parent_id=int(facility_json["parentId"]) if "parentId" in facility_json else None
    )
