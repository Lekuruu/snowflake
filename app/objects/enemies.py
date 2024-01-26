
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.engine.game import Game

from app.objects import (
    SoundCollection,
    AssetCollection,
    GameObject,
    Sound,
    Asset
)

class Sly(GameObject):
    range: int = 3
    attack: int = 4
    move: int = 3

    assets = AssetCollection({
        Asset.from_name('sly_idle_anim'),
        Asset.from_name('sly_attack_anim'),
        Asset.from_name('sly_move_anim'),
        Asset.from_name('sly_hit_anim'),
        Asset.from_name('sly_ko_anim'),
        Asset.from_name('sly_projectile_anim'),
        Asset.from_name('sly_daze_anim'),
        Asset.from_name('snowman_spawn_anim')
    })
    sounds = SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_footstepsly_loop'),
        Sound.from_name('sfx_mg_2013_cjsnow_attacksly'),
        Sound.from_name('sfx_mg_2013_cjsnow_impactsly'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmanslyhit'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmenappear')
    })

    def __init__(self, game: "Game", x: int = 0, y: int = 0, id: int = -1) -> None:
        super().__init__(game, 'Sly', x, y, id, Sly.assets, Sly.sounds)
        self.hp = 30

class Scrap(GameObject):
    range: int = 2
    attack: int = 5
    move: int = 2

    assets = AssetCollection({
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
       Asset.from_name('scrap_dazed_anim'),
       Asset.from_name('snowman_spawn_anim')
    })
    sounds = SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_snowmanscraphit'),
        Sound.from_name('sfx_mg_2013_cjsnow_impactscrap'),
        Sound.from_name('sfx_mg_2013_cjsnow_footstepscrap_loop'),
        Sound.from_name('sfx_mg_2013_cjsnow_attackscrap'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmenappear')
    })

    def __init__(self, game: "Game", x: int = 0, y: int = 0, id: int = -1) -> None:
        super().__init__(game, 'Scrap', x, y, id, Scrap.assets, Scrap.sounds)
        self.hp = 45

class Tank(GameObject):
    range: int = 1
    attack: int = 10
    move: int = 1

    assets = AssetCollection({
        Asset.from_name('tank_swipe_horiz_anim'),
        Asset.from_name('tank_swipe_vert_anim'),
        Asset.from_name('tank_idle_anim'),
        Asset.from_name('tank_attack_anim'),
        Asset.from_name('tank_hit_anim'),
        Asset.from_name('tank_move_anim'),
        Asset.from_name('tank_knockout_anim'),
        Asset.from_name('tank_daze_anim'),
        Asset.from_name('snowman_spawn_anim')
    })
    sounds = SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_snowmantankhit'),
        Sound.from_name('sfx_mg_2013_cjsnow_footsteptank'),
        Sound.from_name('sfx_mg_2013_cjsnow_attacktank'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmenappear')
    })

    def __init__(self, game: "Game", x: int = 0, y: int = 0, id: int = -1) -> None:
        super().__init__(game, 'Tank', x, y, id, Tank.assets, Tank.sounds)
        self.hp = 60
