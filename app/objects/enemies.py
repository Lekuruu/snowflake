
from dataclasses import dataclass, field
from app.objects import (
    SoundCollection,
    AssetCollection,
    GameObject,
    Sound,
    Asset
)

@dataclass
class Sly(GameObject):
    name: str = 'Sly'
    assets: AssetCollection = field(default_factory=lambda: AssetCollection({
        Asset.from_name('sly_idle_anim'),
        Asset.from_name('sly_attack_anim'),
        Asset.from_name('sly_move_anim'),
        Asset.from_name('sly_hit_anim'),
        Asset.from_name('sly_ko_anim'),
        Asset.from_name('sly_projectile_anim'),
        Asset.from_name('sly_daze_anim')
    }))
    sounds: SoundCollection = field(default_factory=lambda: SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_footstepsly_loop'),
        Sound.from_name('sfx_mg_2013_cjsnow_attacksly'),
        Sound.from_name('sfx_mg_2013_cjsnow_impactsly'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmanslyhit')
    }))

    def __eq__(self, other: "GameObject") -> bool:
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

@dataclass
class Scrap(GameObject):
    name: str = 'Scrap'
    assets: AssetCollection = field(default_factory=lambda: AssetCollection({
        Asset.from_name('scrap_idle_anim'),
        Asset.from_name('scrap_attack_anim'),
        Asset.from_name('scrap_attackeffect_anim'),
        Asset.from_name('scrap_attacklittleeffect_anim'),
        Asset.from_name('scrap_projectileeast_anim'),
        Asset.from_name('scrap_projectilenorth_anim'),
        Asset.from_name('scrap_projectilenortheast_anim'),
        Asset.from_name('scrap_hit_anim'),
        Asset.from_name('scrap_move_anim'),
        Asset.from_name('scrap_ko_anim'),
        Asset.from_name('scrap_dazed_anim')
    }))
    sounds: SoundCollection = field(default_factory=lambda: SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_snowmanscraphit'),
        Sound.from_name('sfx_mg_2013_cjsnow_impactscrap'),
        Sound.from_name('sfx_mg_2013_cjsnow_footstepscrap_loop'),
        Sound.from_name('sfx_mg_2013_cjsnow_attackscrap')
    }))

    def __eq__(self, other: "GameObject") -> bool:
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

@dataclass
class Tank(GameObject):
    name: str = 'Tank'
    assets: AssetCollection = field(default_factory=lambda: AssetCollection({
        Asset.from_name('tank_swipe_horiz_anim'),
        Asset.from_name('tank_swipe_vert_anim'),
        Asset.from_name('tank_idle_anim_flaxp0000'),
        Asset.from_name('tank_attack_anim_flaxp0000'),
        Asset.from_name('tank_hit_anim'),
        Asset.from_name('tank_move_anim'),
        Asset.from_name('tank_knockout_anim'),
        Asset.from_name('tank_daze_anim')
    }))
    sounds: SoundCollection = field(default_factory=lambda: SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_snowmantankhit'),
        Sound.from_name('sfx_mg_2013_cjsnow_footsteptank'),
        Sound.from_name('sfx_mg_2013_cjsnow_attacktank')
    }))

    def __eq__(self, other: "GameObject") -> bool:
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

@dataclass
class Tusk(GameObject):
    name: str = 'Tusk'
    assets: AssetCollection = field(default_factory=lambda: AssetCollection({
        Asset.from_name('tusk_background_under'),
        Asset.from_name('tusk_idle_anim'),
        Asset.from_name('tusk_hit_anim'),
        Asset.from_name('tusk_pushattack_anim'),
        Asset.from_name('tusk_lose_anim'),
        Asset.from_name('tusk_win_anim'),
        Asset.from_name('tusk_icicle_drop_anim'),
        Asset.from_name('tusk_stun_anim'),
        Asset.from_name('tusk_iciclesummon1_anim'),
        Asset.from_name('tusk_iciclesummon2_anim'),
    }))
    sounds: SoundCollection = field(default_factory=lambda: SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_tusklaugh'),
        Sound.from_name('sfx_mg_2013_cjsnow_hittusk'),
        Sound.from_name('sfx_mg_2013_cjsnow_attacktuskicicle01'),
        Sound.from_name('sfx_mg_2013_cjsnow_attacktuskicicle02'),
        Sound.from_name('sfx_mg_2013_cjsnow_attacktuskearthquake')
    }))

    def __eq__(self, other: "GameObject") -> bool:
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
