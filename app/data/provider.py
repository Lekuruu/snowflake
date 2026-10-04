
from __future__ import annotations

from abc import ABC, abstractmethod
from importlib import import_module
from typing import Mapping, Sequence

from .models import (
    PowerCardCounts,
    PenguinData,
    StampData,
    CardData
)

class DataProvider(ABC):
    """Abstracted data operations used by snowflake"""

    @abstractmethod
    def fetch_penguin(self, penguin_id: int) -> PenguinData | None:
        ...

    @abstractmethod
    def fetch_session_token(self, penguin_id: int) -> str | None:
        ...

    @abstractmethod
    def fetch_random_penguin(self) -> PenguinData | None:
        ...

    @abstractmethod
    def fetch_power_cards(self, penguin_id: int, element: str) -> list[CardData]:
        ...

    @abstractmethod
    def fetch_power_card_counts(self, penguin_id: int) -> PowerCardCounts:
        ...

    @abstractmethod
    def fetch_stamps(self, group_id: int) -> list[StampData]:
        ...

    @abstractmethod
    def fetch_penguin_stamps(self, penguin_id: int, group_id: int | None = None) -> list[StampData]:
        ...

    @abstractmethod
    def award_stamp(self, penguin_id: int, stamp_id: int) -> StampData | None:
        """Award a stamp and return it, or return `None` if not awarded"""
        ...

    @abstractmethod
    def has_completed_stamp_group(self, penguin_id: int, group_id: int) -> bool:
        """Return whether the penguin has completed the stamp group"""
        ...

    @abstractmethod
    def apply_payout(
        self,
        penguin_id: int,
        updates: Mapping[str, int],
        item_ids: Sequence[int] = (),
        stamp_ids: Sequence[int] = ()
    ) -> list[StampData]:
        """Apply one player's payout and return newly awarded stamps"""
        ...


def load_data_provider(reference: str) -> DataProvider:
    """
    Attempt to create a provider from the reference,
    e.g. `app.data.providers.houdini:HoudiniDataProvider`
    """
    module_name, separator, attribute_name = reference.partition(":")

    if not separator or not module_name or not attribute_name:
        raise ValueError("DATA_PROVIDER must use the format 'module:attribute'")

    module = import_module(module_name)
    factory = getattr(module, attribute_name)
    provider = factory()

    if not isinstance(provider, DataProvider):
        raise TypeError(
            f"{reference} did not create a DataProvider instance"
        )

    return provider
