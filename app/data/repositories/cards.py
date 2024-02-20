
from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import func
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
    element: str,
    session: Session | None = None
) -> List[Card]:
    return session.query(Card) \
        .join(PenguinCard) \
        .filter(PenguinCard.penguin_id == penguin_id) \
        .filter(Card.element == element) \
        .all()

@session_wrapper
def fetch_power_cards_by_penguin_id(
    penguin_id: int,
    element: str,
    session: Session | None = None
) -> List[Card]:
    # Subquery to generate series of cards, based on quantity
    subquery = session.query(
            PenguinCard.card_id,
            func.generate_series(1, PenguinCard.quantity).label('index')
        ) \
        .filter(PenguinCard.penguin_id == penguin_id) \
        .subquery()

    return session.query(Card) \
        .join(subquery, Card.id == subquery.c.card_id) \
        .filter(Card.element == element) \
        .filter(Card.power_id > 0) \
        .all()

@session_wrapper
def fetch_count(
    penguin_id: int,
    element: str,
    session: Session | None = None
) -> int:
    return session.query(func.sum(PenguinCard.quantity)) \
        .join(Card) \
        .filter(PenguinCard.penguin_id == penguin_id) \
        .filter(Card.element == element) \
        .scalar() or 0

@session_wrapper
def fetch_power_card_count(
    penguin_id: int,
    element: str,
    session: Session | None = None
) -> int:
    return session.query(func.sum(PenguinCard.quantity)) \
        .join(Card) \
        .filter(PenguinCard.penguin_id == penguin_id) \
        .filter(Card.element == element) \
        .filter(Card.power_id > 0) \
        .scalar() or 0
