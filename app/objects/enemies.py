
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

class Enemy(GameObject):
    name: str = 'Enemy'
    max_hp: int = 0
    range: int = 0
    attack: int = 0
    move: int = 0

    assets = AssetCollection()
    sounds = SoundCollection()

    def __init__(
        self,
        game: "Game",
        x: int = 0,
        y: int = 0
    ) -> None:
        super().__init__(game, self.__class__.name, x, y)
        self.assets = self.__class__.assets
        self.sounds = self.__class__.sounds
        self.attack = self.__class__.attack
        self.range = self.__class__.range
        self.max_hp = self.__class__.max_hp
        self.hp = self.max_hp

    def spawn(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmenappear')
        self.spawn_animation()
        self.idle_animation()

    def spawn_animation(self) -> None:
        self.animate_object(
            'snowman_spawn_anim',
            play_style='play_once'
        )

    def idle_animation(self) -> None:
        self.animate_object(
            f'{self.name.lower()}_idle_anim',
            play_style='loop'
        )

class Sly(Enemy):
    name: str = 'Sly'
    max_hp: int = 30
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

class Scrap(Enemy):
    name: str = 'Scrap'
    max_hp: int = 45
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

class Tank(Enemy):
    name: str = 'Tank'
    max_hp: int = 60
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
