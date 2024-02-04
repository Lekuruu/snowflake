
from __future__ import annotations

from sqlalchemy.orm import Session
from typing import List

from ..objects import Card, PenguinCard
from .wrapper import session_wrapper

@session_wrapper
def fetch_one(id: int, session: Session | None = None) -> Card:
    return session.query(Card) \
        .filter(Card.id == id) \
        .first()

@session_wrapper
def fetch_all(session: Session | None = None) -> List[Card]:
    return session.query(Card) \
        .all()

@session_wrapper
def fetch_by_element(element: str, session: Session | None = None) -> List[Card]:
    return session.query(Card) \
        .filter(Card.element == element) \
        .all()

@session_wrapper
def fetch_power_cards(session: Session | None = None) -> List[Card]:
    return session.query(Card) \
        .filter(Card.power_id > 0) \
        .all()

@session_wrapper
def fetch_by_penguin_id(
    penguin_id: int,
    element: str | None = None,
    session: Session | None = None
) -> List[Card]:
    query = session.query(Card) \
        .join(PenguinCard) \
        .filter(PenguinCard.penguin_id == penguin_id)

    if element:
        query = query.filter(Card.element == element)

    return query.all()

@session_wrapper
def fetch_power_cards_by_penguin_id(
    penguin_id: int,
    element: str | None = None,
    session: Session | None = None
) -> List[Card]:
    query = session.query(Card) \
        .join(PenguinCard) \
        .filter(PenguinCard.penguin_id == penguin_id) \
        .filter(Card.power_id > 0)

    if element:
        query = query.filter(Card.element == element)

    return query.all()
