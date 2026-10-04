
from __future__ import annotations
from typing import Mapping, Sequence

from urllib.parse import quote_plus

from redis import Redis
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, select, update

from app.data.models import CardData, PenguinData, PowerCardCounts, StampData
from app.data.provider import DataProvider

from .models import (
    Card,
    Penguin,
    PenguinCard,
    PenguinItem,
    PenguinStamp,
    Stamp
)

import config

class HoudiniDataProvider(DataProvider):
    """Data provider for the standard Houdini PostgreSQL & Redis stack"""

    def __init__(self, engine: Engine | None = None, redis: Redis | None = None) -> None:
        self.engine = engine or self.create_engine()

        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False
        )

        self.redis = redis or Redis(
            config.REDIS_HOST,
            config.REDIS_PORT,
            config.REDIS_DB,
            config.REDIS_PASSWORD
        )

    @staticmethod
    def create_engine() -> Engine:
        username = quote_plus(config.POSTGRES_USER)
        password = quote_plus(config.POSTGRES_PASSWORD)
        database = quote_plus(config.POSTGRES_DBNAME)

        return create_engine(
            f"postgresql://{username}:{password}@"
            f"{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{database}",
            pool_pre_ping=True,
            pool_recycle=900,
            pool_timeout=5
        )

    @staticmethod
    def penguin(row: Penguin) -> PenguinData:
        return PenguinData(
            id=row.id,
            nickname=row.nickname,
            approval_en=row.approval_en,
            rejection_en=row.rejection_en,
            snow_ninja_rank=row.snow_ninja_rank,
            snow_ninja_progress=row.snow_ninja_progress,
            coins=row.coins,
            snow_progress_fire_wins=row.snow_progress_fire_wins,
            snow_progress_water_wins=row.snow_progress_water_wins,
            snow_progress_snow_wins=row.snow_progress_snow_wins
        )

    @staticmethod
    def card(row: Card) -> CardData:
        return CardData(
            id=row.id,
            name=row.name,
            set_id=row.set_id,
            power_id=row.power_id,
            element=row.element,
            color=row.color,
            value=row.value,
            description=row.description
        )

    @staticmethod
    def stamp(row: Stamp) -> StampData:
        return StampData(
            id=row.id,
            name=row.name,
            group_id=row.group_id,
            member=row.member,
            rank=row.rank,
            description=row.description
        )

    def fetch_penguin(self, penguin_id: int) -> PenguinData | None:
        with self.session_factory() as session:
            row = session.get(Penguin, penguin_id)
            return self.penguin(row) if row else None

    def fetch_session_token(self, penguin_id: int) -> str | None:
        token = self.redis.get(f"{penguin_id}.mpsession")

        if token is None:
            return None

        if isinstance(token, bytes):
            return token.decode()

        return str(token)

    def fetch_random_penguin(self) -> PenguinData | None:
        with self.session_factory() as session:
            row = session.scalars(
                select(Penguin).
                order_by(func.random()).
                limit(1)
            ).first()

            return (
                self.penguin(row)
                if row else None
            )

    def fetch_power_cards(self, penguin_id: int, element: str) -> list[CardData]:
        with self.session_factory() as session:
            query = select(Card, PenguinCard.quantity) \
                .join(
                    PenguinCard, Card.id == PenguinCard.card_id
                ) \
                .where(
                    PenguinCard.penguin_id == penguin_id,
                    Card.element == element,
                    Card.power_id > 0
                )

            return [
                self.card(card)
                for card, quantity in session.execute(query).all()
                for _ in range(quantity)
            ]

    def fetch_power_card_counts(self, penguin_id: int) -> PowerCardCounts:
        with self.session_factory() as session:
            def count(element: str) -> int:
                value = session.scalar(
                    select(func.sum(PenguinCard.quantity)).
                    join(Card, Card.id == PenguinCard.card_id).
                    where(
                        PenguinCard.penguin_id == penguin_id,
                        Card.element == element,
                        Card.power_id > 0
                    )
                )
                return int(value or 0)

            return PowerCardCounts(
                fire=count("f"),
                water=count("w"),
                snow=count("s")
            )

    def fetch_stamps(self, group_id: int) -> list[StampData]:
        with self.session_factory() as session:
            rows = session.scalars(
                select(Stamp).
                where(Stamp.group_id == group_id)
            ).all()

            return [
                self.stamp(row)
                for row in rows
            ]

    def fetch_penguin_stamps(self, penguin_id: int, group_id: int | None = None) -> list[StampData]:
        with self.session_factory() as session:
            statement = (
                select(Stamp).
                join(PenguinStamp, Stamp.id == PenguinStamp.stamp_id).
                where(PenguinStamp.penguin_id == penguin_id)
            )

            if group_id is not None:
                statement = statement.where(Stamp.group_id == group_id)

            rows = session.scalars(statement).all()
            return [self.stamp(row) for row in rows]

    def award_stamp(self, penguin_id: int, stamp_id: int) -> StampData | None:
        with self.session_factory.begin() as session:
            stamp = session.get(Stamp, stamp_id)
            if stamp is None:
                return None

            owned_stamp = session.get(
                PenguinStamp,
                {
                    "penguin_id": penguin_id,
                    "stamp_id": stamp_id
                }
            )
            if owned_stamp is not None:
                return None

            session.add(PenguinStamp(
                penguin_id=penguin_id,
                stamp_id=stamp_id
            ))
            session.flush()
            return self.stamp(stamp)

    def has_completed_stamp_group(
        self,
        penguin_id: int,
        group_id: int
    ) -> bool:
        with self.session_factory() as session:
            total = session.scalar(
                select(func.count()).
                select_from(Stamp).
                where(Stamp.group_id == group_id)
            )
            collected = session.scalar(
                select(func.count()).
                select_from(Stamp).
                join(PenguinStamp, Stamp.id == PenguinStamp.stamp_id).
                where(
                    PenguinStamp.penguin_id == penguin_id,
                    Stamp.group_id == group_id
                )
            )
            return (total or 0) == (collected or 0)

    def apply_payout(
        self,
        penguin_id: int,
        updates: Mapping[str, int],
        item_ids: Sequence[int] = (),
        stamp_ids: Sequence[int] = ()
    ) -> list[StampData]:
        awarded_stamps = []

        with self.session_factory.begin() as session:
            if updates:
                session.execute(
                    update(Penguin).
                    where(Penguin.id == penguin_id).
                    values(**dict(updates))
                )

            for item_id in dict.fromkeys(item_ids):
                owned_item = session.get(
                    PenguinItem,
                    {
                        "penguin_id": penguin_id,
                        "item_id": item_id
                    }
                )
                if owned_item is None:
                    session.add(PenguinItem(
                        penguin_id=penguin_id,
                        item_id=item_id
                    ))

            for stamp_id in dict.fromkeys(stamp_ids):
                stamp = session.get(Stamp, stamp_id)
                if stamp is None:
                    continue

                owned_stamp = session.get(
                    PenguinStamp,
                    {
                        "penguin_id": penguin_id,
                        "stamp_id": stamp_id
                    }
                )
                if owned_stamp is not None:
                    continue

                session.add(PenguinStamp(
                    penguin_id=penguin_id,
                    stamp_id=stamp_id
                ))
                awarded_stamps.append(self.stamp(stamp))

        return awarded_stamps
