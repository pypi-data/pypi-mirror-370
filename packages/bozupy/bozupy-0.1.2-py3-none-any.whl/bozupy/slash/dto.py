from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from ..cybozu.constant import Locales


@dataclass
class Org:
    code: str
    id: int
    name: str
    parent_code: str | None = None
    description: str | None = None


@dataclass
class Group:
    code: str
    id: int
    name: str
    description: str | None = None


@dataclass
class User:
    code: str
    id: int
    created_at: datetime
    updated_at: datetime
    is_valid: bool
    name: str
    locale: Locales
    timezone: str
    description: str | None = None
    mail_address: str | None = None
    employee_number: str | None = None
    url: str | None = None
    birth_date: date | None = None
    join_date: date | None = None
    primary_org_id: int | None = None
