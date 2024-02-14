
# Modified sqlalchemy classes from solero/houdini:
# https://github.com/solero/houdini/tree/master/houdini/data/

from __future__ import annotations

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
from sqlalchemy import (
    SmallInteger,
    ForeignKey,
    DateTime,
    Interval,
    Boolean,
    Integer,
    Column,
    String,
    Date,
    Time,
    CHAR
)

Base = declarative_base()

__all__ = [
    'Base',
    'Penguin',
    'Card',
    'CardStarterDeck',
    'PenguinCard',
    'Stamp',
    'StampGroup',
    'CoverStamp',
    'CoverItem',
    'PenguinStamp',
    'Item',
    'PenguinItem'
]

class Penguin(Base):
    __tablename__ = 'penguin'

    id = Column(Integer, primary_key=True, server_default=text("nextval('\"penguin_id_seq\"'::regclass)"))
    username = Column(String(12), nullable=False, unique=True)
    nickname = Column(String(30), nullable=False)
    password = Column(CHAR(60), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    registration_date = Column(DateTime, nullable=False, server_default=text("now()"))
    active = Column(Boolean, nullable=False, server_default=text("false"))
    safe_chat = Column(Boolean, nullable=False, server_default=text("false"))
    last_paycheck = Column(DateTime, nullable=False, server_default=text("now()"))
    minutes_played = Column(Integer, nullable=False, server_default=text("0"))
    moderator = Column(Boolean, nullable=False, server_default=text("false"))
    stealth_moderator = Column(Boolean, nullable=False, server_default=text("false"))
    character = Column(ForeignKey('character.id', ondelete='CASCADE', onupdate='CASCADE'))
    igloo = Column(ForeignKey('penguin_igloo_room.id', ondelete='CASCADE', onupdate='CASCADE'))
    coins = Column(Integer, nullable=False, server_default=text("500"))
    color = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    head = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    face = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    neck = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    body = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    hand = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    feet = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    photo = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    flag = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'))
    permaban = Column(Boolean, nullable=False, server_default=text("false"))
    book_modified = Column(SmallInteger, nullable=False, server_default=text("0"))
    book_color = Column(SmallInteger, nullable=False, server_default=text("1"))
    book_highlight = Column(SmallInteger, nullable=False, server_default=text("1"))
    book_pattern = Column(SmallInteger, nullable=False, server_default=text("0"))
    book_icon = Column(SmallInteger, nullable=False, server_default=text("1"))
    agent_status = Column(Boolean, nullable=False, server_default=text("false"))
    field_op_status = Column(SmallInteger, nullable=False, server_default=text("0"))
    career_medals = Column(Integer, nullable=False, server_default=text("0"))
    agent_medals = Column(Integer, nullable=False, server_default=text("0"))
    last_field_op = Column(DateTime, nullable=False, server_default=text("now()"))
    com_message_read_date = Column(DateTime, nullable=False, server_default=text("now()"))
    ninja_rank = Column(SmallInteger, nullable=False, server_default=text("0"))
    ninja_progress = Column(SmallInteger, nullable=False, server_default=text("0"))
    fire_ninja_rank = Column(SmallInteger, nullable=False, server_default=text("0"))
    fire_ninja_progress = Column(SmallInteger, nullable=False, server_default=text("0"))
    water_ninja_rank = Column(SmallInteger, nullable=False, server_default=text("0"))
    water_ninja_progress = Column(SmallInteger, nullable=False, server_default=text("0"))
    snow_ninja_progress = Column(SmallInteger, nullable=False, server_default=text("0"))
    snow_ninja_rank = Column(SmallInteger, nullable=False, server_default=text("0"))
    ninja_matches_won = Column(Integer, nullable=False, server_default=text("0"))
    fire_matches_won = Column(Integer, nullable=False, server_default=text("0"))
    water_matches_won = Column(Integer, nullable=False, server_default=text("0"))
    snow_progress_fire_wins = Column(Integer, nullable=False, server_default=text("0"))
    snow_progress_water_wins = Column(Integer, nullable=False, server_default=text("0"))
    snow_progress_snow_wins = Column(Integer, nullable=False, server_default=text("0"))
    rainbow_adoptability = Column(Boolean, nullable=False, server_default=text("false"))
    has_dug = Column(Boolean, nullable=False, server_default=text("false"))
    puffle_handler = Column(Boolean, nullable=False, server_default=text("false"))
    nuggets = Column(SmallInteger, nullable=False, server_default=text("0"))
    walking = Column(ForeignKey('penguin_puffle.id', ondelete='CASCADE', onupdate='CASCADE'))
    opened_playercard = Column(Boolean, nullable=False, server_default=text("false"))
    special_wave = Column(Boolean, nullable=False, server_default=text("false"))
    special_dance = Column(Boolean, nullable=False, server_default=text("false"))
    special_snowball = Column(Boolean, nullable=False, server_default=text("false"))
    map_category = Column(SmallInteger, nullable=False, server_default=text("0"))
    status_field = Column(Integer, nullable=False, server_default=text("0"))
    timer_active = Column(Boolean, nullable=False, server_default=text("false"))
    timer_start = Column(Time, nullable=False, server_default=text("'00:00:00'::time without time zone"))
    timer_end = Column(Time, nullable=False, server_default=text("'23:59:59'::time without time zone"))
    timer_total = Column(Interval, nullable=False, server_default=text("'01:00:00'::interval"))
    grounded = Column(Boolean, nullable=False, server_default=text("false"))
    approval_en = Column(Boolean, nullable=False, server_default=text("false"))
    approval_pt = Column(Boolean, nullable=False, server_default=text("false"))
    approval_fr = Column(Boolean, nullable=False, server_default=text("false"))
    approval_es = Column(Boolean, nullable=False, server_default=text("false"))
    approval_de = Column(Boolean, nullable=False, server_default=text("false"))
    approval_ru = Column(Boolean, nullable=False, server_default=text("false"))
    rejection_en = Column(Boolean, nullable=False, server_default=text("false"))
    rejection_pt = Column(Boolean, nullable=False, server_default=text("false"))
    rejection_fr = Column(Boolean, nullable=False, server_default=text("false"))
    rejection_es = Column(Boolean, nullable=False, server_default=text("false"))
    rejection_de = Column(Boolean, nullable=False, server_default=text("false"))
    rejection_ru = Column(Boolean, nullable=False, server_default=text("false"))

class Card(Base):
    __tablename__ = 'card'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    set_id = Column(SmallInteger, nullable=False, server_default=text("1"))
    power_id = Column(SmallInteger, nullable=False, server_default=text("0"))
    element = Column(CHAR(1), nullable=False, server_default=text("'s'::bpchar"))
    color = Column(CHAR(1), nullable=False, server_default=text("'b'::bpchar"))
    value = Column(SmallInteger, nullable=False, server_default=text("2"))
    description = Column(String(255), nullable=False, server_default=text("''::character varying"))

    def __repr__(self) -> str:
        return f'{self.id}|{self.element}|{self.value}|{self.color}|{self.power_id}'

class CardStarterDeck(Base):
    __tablename__ = 'card_starter_deck'

    item_id = Column(
        ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False,
        index=True
    )

    card_id = Column(
        ForeignKey('card.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False
    )

    quantity = Column(
        SmallInteger,
        nullable=False,
        server_default=text("1")
    )

class PenguinCard(Base):
    __tablename__ = 'penguin_card'

    penguin_id = Column(
        ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False,
        index=True
    )

    card_id = Column(
        ForeignKey('card.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False
    )

    quantity = Column(SmallInteger, nullable=False, server_default=text("1"))
    member_quantity = Column(SmallInteger, nullable=False, server_default=text("0"))

class Stamp(Base):
    __tablename__ = 'stamp'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    group_id = Column(ForeignKey('stamp_group.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    member = Column(Boolean, nullable=False, server_default=text("false"))
    rank = Column(SmallInteger, nullable=False, server_default=text("1"))
    description = Column(String(255), nullable=False, server_default=text("''::character varying"))

    @property
    def rank_token(self) -> str:
        return {
            1: 'Easy',
            2: 'Medium',
            3: 'Hard',
            4: 'Extreme'
        }.get(self.rank, '')

class StampGroup(Base):
    __tablename__ = 'stamp_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    parent_id = Column(ForeignKey('stamp_group.id', ondelete='CASCADE', onupdate='CASCADE'))

class CoverStamp(Base):
    __tablename__ = 'cover_stamp'

    penguin_id = Column(
        ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False
    )

    stamp_id = Column(
        ForeignKey('stamp.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False
    )

    x = Column(SmallInteger, nullable=False, server_default=text("0"))
    y = Column(SmallInteger, nullable=False, server_default=text("0"))
    rotation = Column(SmallInteger, nullable=False, server_default=text("0"))
    depth = Column(SmallInteger, nullable=False, server_default=text("0"))

class CoverItem(Base):
    __tablename__ = 'cover_item'

    penguin_id = Column(
        ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False
    )

    item_id = Column(
        ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False
    )

    x = Column(SmallInteger, nullable=False, server_default=text("0"))
    y = Column(SmallInteger, nullable=False, server_default=text("0"))
    rotation = Column(SmallInteger, nullable=False, server_default=text("0"))
    depth = Column(SmallInteger, nullable=False, server_default=text("0"))

class PenguinStamp(Base):
    __tablename__ = 'penguin_stamp'

    penguin_id = Column(
        ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False
    )

    stamp_id = Column(
        ForeignKey('stamp.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False
    )

    recent = Column(
        Boolean,
        nullable=False,
        server_default=text("true")
    )

    def __init__(self, penguin_id: int, stamp_id: int):
        self.penguin_id = penguin_id
        self.stamp_id = stamp_id

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(SmallInteger, nullable=False, server_default=text("1"))
    cost = Column(Integer, nullable=False, server_default=text("0"))
    member = Column(Boolean, nullable=False, server_default=text("false"))
    bait = Column(Boolean, nullable=False, server_default=text("false"))
    patched = Column(Boolean, nullable=False, server_default=text("false"))
    legacy_inventory = Column(Boolean, nullable=False, server_default=text("false"))
    vanilla_inventory = Column(Boolean, nullable=False, server_default=text("false"))
    epf = Column(Boolean, nullable=False, server_default=text("false"))
    tour = Column(Boolean, nullable=False, server_default=text("false"))
    release_date = Column(Date, nullable=False, server_default=text("now()"))
    treasure = Column(Boolean, nullable=False, server_default=text("false"))
    innocent = Column(Boolean, nullable=False, server_default=text("false"))

    def is_color(self):
        return self.type == 1

    def is_head(self):
        return self.type == 2

    def is_face(self):
        return self.type == 3

    def is_neck(self):
        return self.type == 4

    def is_body(self):
        return self.type == 5

    def is_hand(self):
        return self.type == 6

    def is_feet(self):
        return self.type == 7

    def is_flag(self):
        return self.type == 8

    def is_photo(self):
        return self.type == 9

    def is_award(self):
        return self.type == 10

class PenguinItem(Base):
    __tablename__ = 'penguin_item'

    penguin_id = Column(
        ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False
    )

    item_id = Column(
        ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
        nullable=False
    )

    def __init__(self, penguin_id: int, item_id: int):
        self.penguin_id = penguin_id
        self.item_id = item_id
