
from __future__ import annotations

from sqlalchemy.orm import Session

from .wrapper import session_wrapper
from ..objects import Stamp

@session_wrapper
def fetch_one(id: int, session: Session | None = None):
    return session.query(Stamp) \
        .filter(Stamp.id == id) \
        .first()

@session_wrapper
def fetch_all_by_group(group_id: int, session: Session | None = None):
    return session.query(Stamp) \
        .filter(Stamp.group_id == group_id) \
        .all()
