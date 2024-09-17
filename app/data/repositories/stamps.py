
from __future__ import annotations

from sqlalchemy.orm import Session
from typing import List

from ..objects import Stamp, PenguinStamp
from .wrapper import session_wrapper

@session_wrapper
def fetch_one(id: int, session: Session = ...) -> Stamp | None:
    return session.query(Stamp) \
        .filter(Stamp.id == id) \
        .first()

@session_wrapper
def fetch_all_by_group(group_id: int, session: Session = ...) -> List[Stamp]:
    return session.query(Stamp) \
        .filter(Stamp.group_id == group_id) \
        .all()

@session_wrapper
def fetch_by_penguin_id(
    penguin_id: int,
    group_id: int | None = None,
    session: Session = ...
) -> List[Stamp]:
    query = session.query(Stamp) \
        .join(PenguinStamp, Stamp.id == PenguinStamp.stamp_id) \
        .filter(PenguinStamp.penguin_id == penguin_id)

    if group_id:
        query = query.filter(Stamp.group_id == group_id)

    return query.all()

@session_wrapper
def add(
    id: int,
    penguin_id: int,
    session: Session = ...
) -> Stamp:
    penguin_stamp = PenguinStamp(penguin_id=penguin_id, stamp_id=id)
    session.add(penguin_stamp)
    session.commit()
    return penguin_stamp

@session_wrapper
def remove(
    id: int,
    penguin_id: int,
    session: Session = ...
) -> int:
    rows = session.query(PenguinStamp) \
        .filter_by(penguin_id=penguin_id, stamp_id=id) \
        .delete()
    session.commit()
    return rows

@session_wrapper
def exists(
    id: int,
    penguin_id: int,
    session: Session = ...
) -> bool:
    return session.query(PenguinStamp) \
        .filter_by(penguin_id=penguin_id, stamp_id=id) \
        .count() > 0

@session_wrapper
def completed_group(
    penguin_id: int,
    group_id: int,
    session: Session = ...
) -> bool:
    total = session.query(Stamp) \
        .filter(Stamp.group_id == group_id) \
        .count()

    collected = session.query(Stamp) \
        .join(PenguinStamp, Stamp.id == PenguinStamp.stamp_id) \
        .filter(PenguinStamp.penguin_id == penguin_id) \
        .filter(Stamp.group_id == group_id) \
        .count()

    return total == collected
