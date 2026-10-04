
from __future__ import annotations
from typing import Mapping, Sequence
from dataclasses import replace

from app.data.models import CardData, PenguinData, PowerCardCounts, StampData
from app.data.provider import DataProvider
from app.data.constants import Stamps


class DummyDataProvider(DataProvider):
    """In-memory data provider for development"""

    def __init__(self, session_token: str = "dummy") -> None:
        self.session_token = session_token
        self.penguins: dict[int, PenguinData] = {}
        self.penguin_items: dict[int, set[int]] = {}
        self.penguin_stamps: dict[int, set[int]] = {}

        self.cards = {
            "f": self.create_cards(
                id_start=1000,
                name="Debug Fire Card",
                element="f",
                color="r"
            ),
            "w": self.create_cards(
                id_start=2000,
                name="Debug Water Card",
                element="w",
                color="b"
            ),
            "s": self.create_cards(
                id_start=3000,
                name="Debug Snow Card",
                element="s",
                color="p"
            )
        }
        self.stamps = {
            stamp_id: StampData(
                id=stamp_id,
                name=f"Debug Stamp {stamp_id}",
                group_id=60,
                member=False,
                rank=1,
                description="Dummy stamp"
            )
            for stamp_id in Stamps
        }

    @classmethod
    def create_cards(
        cls,
        id_start: int,
        name: str,
        element: str,
        color: str,
        amount: int = 8
    ) -> list[CardData]:
        return [
            CardData(
                id=id_start + index,
                name=f"{name} {index + 1}",
                set_id=1,
                power_id=1,
                element=element,
                color=color,
                value=12,
                description="Dummy power card"
            )
            for index in range(amount)
        ]

    def create_penguin(self, penguin_id: int) -> PenguinData:
        penguin = PenguinData(
            id=penguin_id,
            nickname=(
                "Debug Bot" if penguin_id == 0 else
                f"Debug {penguin_id}"
            ),
            approval_en=True,
            rejection_en=False,
            snow_ninja_rank=13,
            snow_ninja_progress=0,
            coins=69420
        )
        self.penguins[penguin_id] = penguin
        return penguin

    def get_or_create_penguin(self, penguin_id: int) -> PenguinData:
        return self.penguins.get(penguin_id) or self.create_penguin(penguin_id)

    def fetch_penguin(self, penguin_id: int) -> PenguinData | None:
        return replace(self.get_or_create_penguin(penguin_id))

    def fetch_session_token(self, penguin_id: int) -> str | None:
        return self.session_token

    def fetch_random_penguin(self) -> PenguinData | None:
        return replace(self.get_or_create_penguin(0))

    def fetch_power_cards(self, penguin_id: int, element: str) -> list[CardData]:
        return [replace(card) for card in self.cards.get(element, [])]

    def fetch_power_card_counts(self, penguin_id: int) -> PowerCardCounts:
        return PowerCardCounts(
            fire=len(self.cards["f"]),
            water=len(self.cards["w"]),
            snow=len(self.cards["s"])
        )

    def fetch_stamps(self, group_id: int) -> list[StampData]:
        return [
            replace(stamp)
            for stamp in self.stamps.values()
            if stamp.group_id == group_id
        ]

    def fetch_penguin_stamps(
        self,
        penguin_id: int,
        group_id: int | None = None
    ) -> list[StampData]:
        owned_stamps = self.penguin_stamps.get(
            penguin_id,
            set()
        )
        return [
            replace(stamp)
            for stamp_id, stamp in self.stamps.items()
            if stamp_id in owned_stamps
            and (group_id is None or stamp.group_id == group_id)
        ]

    def award_stamp(
        self,
        penguin_id: int,
        stamp_id: int
    ) -> StampData | None:
        stamp = self.stamps.get(stamp_id)
        owned_stamps = self.penguin_stamps.setdefault(penguin_id, set())

        if stamp is None or stamp_id in owned_stamps:
            return None

        owned_stamps.add(stamp_id)
        return replace(stamp)

    def has_completed_stamp_group(
        self,
        penguin_id: int,
        group_id: int
    ) -> bool:
        owned_stamps = self.penguin_stamps.get(penguin_id, set())
        group_stamps = {
            stamp.id
            for stamp in self.stamps.values()
            if stamp.group_id == group_id
        }
        return group_stamps.issubset(owned_stamps)

    def apply_payout(
        self,
        penguin_id: int,
        updates: Mapping[str, int],
        item_ids: Sequence[int] = (),
        stamp_ids: Sequence[int] = ()
    ) -> list[StampData]:
        penguin = replace(self.get_or_create_penguin(penguin_id))
        items = self.penguin_items.get(penguin_id, set()).copy()
        owned_stamps = self.penguin_stamps.get(penguin_id, set()).copy()
        awarded_stamps = []

        for field, value in updates.items():
            assert hasattr(penguin, field), f"Unknown penguin field: {field}"
            setattr(penguin, field, value)

        items.update(item_ids)

        for stamp_id in dict.fromkeys(stamp_ids):
            stamp = self.stamps.get(stamp_id)
            if stamp is None or stamp_id in owned_stamps:
                continue

            owned_stamps.add(stamp_id)
            awarded_stamps.append(replace(stamp))

        self.penguins[penguin_id] = penguin
        self.penguin_items[penguin_id] = items
        self.penguin_stamps[penguin_id] = owned_stamps
        return awarded_stamps
