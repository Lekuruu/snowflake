
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

class Ninja(GameObject):
    name: str = 'Ninja'
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
        super().__init__(game, self.__class__.name, x, y, grid=True)
        self.assets = self.__class__.assets
        self.sounds = self.__class__.sounds
        self.attack = self.__class__.attack
        self.range = self.__class__.range
        self.max_hp = 100
        self.hp = 100

        self.initialize_objects()

    def initialize_objects(self) -> None:
        self.ghost = GameObject.from_asset(
            f'{self.name.lower()}ninja_move_ghost',
            self.game,
            grid=True,
            on_click=self.on_ghost_click
        )

        self.confirm = GameObject.from_asset(
            'confirm',
            self.game
        )

    def idle_animation(self) -> None:
        self.animate_object(
            f'{self.name.lower()}ninja_idle_anim',
            play_style='loop'
        )

    def place_ghost(self, x: int, y: int) -> None:
        if (self.ghost.x == x) and (self.ghost.y == y):
            self.hide_ghost()
            return

        self.ghost.x = x
        self.ghost.y = y
        self.ghost.place_object()
        self.ghost.place_sprite(self.ghost.name)

    def hide_ghost(self) -> None:
        self.ghost.hide()
        self.ghost.x = self.x
        self.ghost.y = self.y

    def on_ghost_click(self, client, object: GameObject, *args) -> None:
        self.hide_ghost()

class WaterNinja(Ninja):
    name: str = 'Water'
    range: int = 1
    attack: int = 6
    move: int = 3

    assets = AssetCollection({
        Asset.from_name('waterninja_move_ghost'),
        Asset.from_name('waterninja_attack_anim'),
        Asset.from_name('waterninja_idle_anim'),
        Asset.from_name('waterninja_move_anim'),
        Asset.from_name('waterninja_hit_anim'),
        Asset.from_name('waterninja_knockout_intro_anim'),
        Asset.from_name('waterninja_knockout_loop_anim'),
        Asset.from_name('waterninja_celebrate_anim'),
        Asset.from_name('waterninja_powercard_fishdrop_anim'),
        Asset.from_name('waterninja_powercard_summon_anim'),
        Asset.from_name('waterninja_powercard_water_loop_anim'),
        Asset.from_name('waterninja_revived_anim'),
        Asset.from_name('waterninja_revive_other_intro_anim'),
        Asset.from_name('waterninja_revive_other_loop_anim'),
        Asset.from_name('waterninja_member_revive')
    })
    sounds = SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_attackwater'),
        Sound.from_name('sfx_mg_2013_cjsnow_attackpowercardwater'),
        Sound.from_name('sfx_mg_2013_cjsnow_footsteppenguin'),
        Sound.from_name('sfx_mg_2013_cjsnow_penguinground'),
        Sound.from_name('sfx_mg_2013_cjsnow_penguinhitsuccess'),
        Sound.from_name('SFX_MG_CJSnow_PowercardReviveStart'),
        Sound.from_name('SFX_MG_CJSnow_PowercardReviveEnd'),
    })

class SnowNinja(Ninja):
    name: str = 'Snow'
    range: int = 1
    attack: int = 10
    move: int = 2

    assets = AssetCollection({
        Asset.from_name('snowninja_move_ghost'),
        Asset.from_name('snowninja_idle_anim'),
        Asset.from_name('snowninja_attack_anim'),
        Asset.from_name('snowninja_heal_anim'),
        Asset.from_name('snowninja_hit_anim'),
        Asset.from_name('snowninja_kointro_anim'),
        Asset.from_name('snowninja_koloop_anim'),
        Asset.from_name('snowninja_move_anim'),
        Asset.from_name('snowninja_hit_anim'),
        Asset.from_name('snowninja_celebrate_anim'),
        Asset.from_name('snowninja_beam_anim_'),
        Asset.from_name('snowninja_powercard_anim'),
        Asset.from_name('snowninja_projectileangle_anim'),
        Asset.from_name('snowninja_projectilehoriz_anim'),
        Asset.from_name('snowninja_projectilevert_anim'),
        Asset.from_name('snowninja_revive_anim_'),
        Asset.from_name('snowninja_reviveothersintro_anim'),
        Asset.from_name('snowninja_reviveothersloop_anim'),
        Asset.from_name('snowninja_member_revive')
    })
    sounds = SoundCollection({
       Sound.from_name('sfx_mg_2013_cjsnow_attacksnow'),
       Sound.from_name('sfx_mg_2013_cjsnow_attackpowercardsnow'),
       Sound.from_name('sfx_mg_2013_cjsnow_footsteppenguin'),
       Sound.from_name('sfx_mg_2013_cjsnow_penguinground'),
       Sound.from_name('sfx_mg_2013_cjsnow_penguinhitsuccess'),
       Sound.from_name('SFX_MG_CJSnow_PowercardReviveStart'),
       Sound.from_name('SFX_MG_CJSnow_PowercardReviveEnd'),
    })

class FireNinja(Ninja):
    name: str = 'Fire'
    range: int = 2
    attack: int = 8
    move: int = 2

    assets = AssetCollection({
        Asset.from_name('fireninja_move_ghost'),
        Asset.from_name('fireninja_idle_anim'),
        Asset.from_name('fireninja_move_anim'),
        Asset.from_name('fireninja_hit_anim'),
        Asset.from_name('fireninja_attack_anim'),
        Asset.from_name('fireninja_powerbottle_anim'),
        Asset.from_name('fireninja_powerskyfire_anim'),
        Asset.from_name('fireninja_projectile_angleup_anim'),
        Asset.from_name('fireninja_projectile_angledown_anim'),
        Asset.from_name('fireninja_projectile_down_anim'),
        Asset.from_name('fireninja_projectile_downfar_anim'),
        Asset.from_name('fireninja_projectile_right_anim'),
        Asset.from_name('fireninja_projectile_rightfar_anim'),
        Asset.from_name('fireninja_projectile_up_anim'),
        Asset.from_name('fireninja_projectile_upfar_anim'),
        Asset.from_name('fireninja_celebratestart_anim'),
        Asset.from_name('fireninja_celebrateloop_anim'),
        Asset.from_name('fireninja_kostart_anim'),
        Asset.from_name('fireninja_koloop_anim'),
        Asset.from_name('fireninja_revived_anim'),
        Asset.from_name('fireninja_reviveother_anim'),
        Asset.from_name('fireninja_reviveotherloop_anim'),
        Asset.from_name('fireninja_power_anim'),
        Asset.from_name('fireninja_member_revive')
    })
    sounds = SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_attackfire'),
        Sound.from_name('sfx_mg_2013_cjsnow_attackpowercardfire'),
        Sound.from_name('sfx_mg_2013_cjsnow_footsteppenguinfire'),
        Sound.from_name('sfx_mg_2013_cjsnow_penguinground'),
        Sound.from_name('sfx_mg_2013_cjsnow_penguinhitsuccess'),
        Sound.from_name('SFX_MG_CJSnow_PowercardReviveStart'),
        Sound.from_name('SFX_MG_CJSnow_PowercardReviveEnd'),
    })
