
from app.engine.game import Game
from app.objects import (
    SoundCollection,
    AssetCollection,
    GameObject,
    Sound,
    Asset
)

from dataclasses import dataclass
from typing import Set

class SlyAssets(AssetCollection):
    def __init__(self) -> None:
        super().__init__()
        super().update({
            Asset.from_name('sly_idle_anim'),
            Asset.from_name('sly_attack_anim'),
            Asset.from_name('sly_move_anim'),
            Asset.from_name('sly_hit_anim'),
            Asset.from_name('sly_ko_anim'),
            Asset.from_name('sly_projectile_anim'),
            Asset.from_name('sly_daze_anim')
        })

class SlySounds(SoundCollection):
    def __init__(self) -> None:
        super().__init__()
        super().update({
            Sound.from_name('sfx_mg_2013_cjsnow_footstepsly_loop'),
            Sound.from_name('sfx_mg_2013_cjsnow_attacksly'),
            Sound.from_name('sfx_mg_2013_cjsnow_impactsly'),
            Sound.from_name('sfx_mg_2013_cjsnow_snowmanslyhit'),
            Sound.from_name('sly_projectile')
        })

@dataclass
class Sly(GameObject):
    name: str = 'Sly'
    assets: SlyAssets = SlyAssets()
    sounds: SlySounds = SlySounds()

class ScrapAssets(AssetCollection):
    def __init__(self) -> None:
        super().__init__()
        super().update({
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
        })

class ScrapSounds(SoundCollection):
    def __init__(self) -> None:
        super().__init__()
        super().update({
            Sound.from_name('sfx_mg_2013_cjsnow_snowmanscraphit'),
            Sound.from_name('sfx_mg_2013_cjsnow_impactscrap'),
            Sound.from_name('sfx_mg_2013_cjsnow_footstepscrap_loop'),
            Sound.from_name('sfx_mg_2013_cjsnow_attackscrap')
        })

@dataclass
class Scrap(GameObject):
    name: str = 'Scrap'
    assets: ScrapAssets = ScrapAssets()
    sounds: ScrapSounds = ScrapSounds()

class TankAssets(AssetCollection):
    def __init__(self) -> None:
        super().__init__()
        super().update({
            Asset.from_name('tank_swipe_horiz_anim'),
            Asset.from_name('tank_swipe_vert_anim'),
            Asset.from_name('tank_idle_anim_flaxp0000'),
            Asset.from_name('tank_attack_anim_flaxp0000'),
            Asset.from_name('tank_hit_anim'),
            Asset.from_name('tank_move_anim'),
            Asset.from_name('tank_knockout_anim'),
            Asset.from_name('tank_daze_anim')
        })

class TankSounds(SoundCollection):
    def __init__(self) -> None:
        super().__init__()
        super().update({
            Sound.from_name('sfx_mg_2013_cjsnow_snowmantankhit'),
            Sound.from_name('sfx_mg_2013_cjsnow_footsteptank'),
            Sound.from_name('sfx_mg_2013_cjsnow_attacktank')
        })

@dataclass
class Tank(GameObject):
    name: str = 'Tank'
    assets: TankAssets = TankAssets()
    sounds: TankSounds = TankSounds()
