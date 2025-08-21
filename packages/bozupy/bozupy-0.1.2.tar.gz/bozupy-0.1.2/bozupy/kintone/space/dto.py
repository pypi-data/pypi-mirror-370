from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Space:
    id: int
    default_thread_id: int
    creator_code: str | None
    modifier_code: str | None
    created_at: datetime
    modified_at: datetime
    body: str
    name: str
