
from __future__ import annotations

from sqlalchemy.orm import Session
from typing import List

from ..objects import Stamp, PenguinStamp
from .wrapper import session_wrapper

@session_wrapper
def fetch_one(id: int, session: Session | None = None) -> Stamp | None:
    return session.query(Stamp) \
        .filter(Stamp.id == id) \
        .first()

@session_wrapper
def fetch_all_by_group(group_id: int, session: Session | None = None) -> List[Stamp]:
    return session.query(Stamp) \
        .filter(Stamp.group_id == group_id) \
        .all()

@session_wrapper
def fetch_by_penguin_id(
    penguin_id: int,
    group_id: int | None = None,
    session: Session | None = None
) -> List[Stamp]:
    query = session.query(Stamp) \
        .join(PenguinStamp, Stamp.id == PenguinStamp.stamp_id) \
        .filter(PenguinStamp.penguin_id == penguin_id)

    if group_id:
        query = query.filter(Stamp.group_id == group_id)

    return query.all()
