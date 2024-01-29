
from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.engine.penguin import Penguin
    from app.engine.game import Game

from app.data import MirrorMode, OriginMode
from app.objects.target import Target
from app.objects import (
    SoundCollection,
    AssetCollection,
    GameObject,
    Sound,
    Asset
)

class Ninja(GameObject):
    name: str = 'Ninja'
    max_hp: int = 0
    range: int = 0
    attack: int = 0
    move: int = 0
    move_duration: int = 600

    assets = AssetCollection()
    sounds = SoundCollection()

    def __init__(
        self,
        game: "Game",
        x: int = -1,
        y: int = -1
    ) -> None:
        super().__init__(game, self.__class__.name, x, y, grid=True)
        self.assets = self.__class__.assets
        self.sounds = self.__class__.sounds
        self.attack = self.__class__.attack
        self.range = self.__class__.range
        self.max_hp = self.__class__.max_hp
        self.hp = self.__class__.max_hp

        self.client: "Penguin" = getattr(game, f'{self.name.lower()}')
        self.targets: List["Target"] = []
        self.initialize_objects()

    @property
    def selected_target(self) -> "Target" | None:
        return next((target for target in self.targets if target.selected), None)

    @property
    def placed_ghost(self) -> bool:
        return self.ghost.x != -1 and self.ghost.y != -1

    def initialize_objects(self) -> None:
        self.ghost = GameObject.from_asset(
            f'{self.name.lower()}ninja_move_ghost',
            self.game,
            grid=True,
            x=-1,
            y=-1,
            on_click=self.on_ghost_click
        )
        self.ghost.add_sound('sfx_mg_2013_cjsnow_uiselecttile')

        self.health_bar = GameObject.from_asset(
            'reghealthbar_animation',
            self.game,
            x=self.x + 0.5,
            y=self.y + 1
        )

    def remove_object(self) -> None:
        self.health_bar.remove_object()
        self.ghost.remove_object()
        super().remove_object()

    def move_object(self, x: int, y: int) -> None:
        self.health_bar.move_object(x + 0.5, y + 1, self.move_duration)
        super().move_object(x, y, self.move_duration)
        self.ghost.x = x
        self.ghost.y = y

    def idle_animation(self) -> None:
        self.animate_object(
            f'{self.name.lower()}ninja_idle_anim',
            play_style='loop'
        )

    def move_animation(self) -> None:
        self.animate_object(
            f'{self.name.lower()}ninja_move_anim',
            play_style='play_once'
        )

    def ko_animation(self) -> None:
        self.animate_object(
            f'{self.name.lower()}ninja_kostart_anim',
            play_style='play_once'
        )
        self.animate_object(
            f'{self.name.lower()}ninja_koloop_anim',
            play_style='loop'
        )

    def attack_animation(self, x: int, y: int) -> None:
        ...

    def win_animation(self) -> None:
        if self.name != 'Fire':
            self.animate_object(
                f'{self.name.lower()}ninja_celebrate_anim',
                play_style='loop',
                reset=True
            )
            return

        self.animate_object(
            f'{self.name.lower()}ninja_celebratestart_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            f'{self.name.lower()}ninja_celebrateloop_anim',
            play_style='loop'
        )

    def revive_animation(self) -> None:
        # NOTE: The revive animation seems to have a slight offset from
        #       all the other animations, so we need to adjust the x and y here.
        #       Not sure if there is a better way to do this.

        # Change offset
        self.x = self.x - 0.2
        self.y = self.y - 0.15
        self.place_object()

        # Reset offset after animation is done
        def reset_offset(*args):
            self.x = self.x + 0.2
            self.y = self.y + 0.15
            self.place_object()
            self.idle_animation()

        self.animate_object(
            f'{self.name.lower()}ninja_revived_anim',
            play_style='play_once',
            reset=True,
            callback=reset_offset
        )

    def place_healthbar(self) -> None:
        self.health_bar.place_object()
        self.health_bar.place_sprite(self.health_bar.name)
        self.reset_healthbar()

    def animate_healthbar(self, start_hp: int, end_hp: int, duration: int = 500) -> None:
        backwards = False

        if end_hp > start_hp:
            # Health increased, playing backwards
            backwards = True

            # Swap start and end hp
            start_hp, end_hp = end_hp, start_hp

        start_frame = 60 - int((start_hp / self.max_hp) * 60)
        end_frame = 60 - int((end_hp / self.max_hp) * 60)

        self.health_bar.animate_sprite(
            start_frame-1,
            end_frame-1,
            backwards=backwards,
            duration=duration
        )

    def reset_healthbar(self) -> None:
        self.health_bar.animate_sprite()

    def set_health(self, hp: int) -> None:
        if self.hp <= 0 and hp > 0:
            self.revive_animation()

        hp = max(0, min(hp, self.max_hp))
        self.animate_healthbar(self.hp, hp, duration=500)
        self.hp = hp

        if self.hp <= 0:
            self.ko_animation()

            if not self.client.disconnected:
                self.client.was_ko = True
                self.play_sound('sfx_mg_2013_cjsnow_penguinground')

    def place_ghost(self, x: int, y: int) -> None:
        if self.client.is_ready:
            return

        if not self.game.timer.running:
            return

        if (self.ghost.x == x) and (self.ghost.y == y):
            self.hide_ghost()
            self.show_targets()
            return

        if not self.game.grid.can_move(x, y):
            return

        self.game.grid.move(self.ghost, x, y)
        self.ghost.place_object()
        self.ghost.place_sprite(self.ghost.name)
        self.ghost.play_sound('sfx_mg_2013_cjsnow_uiselecttile')
        self.show_targets()

    def hide_ghost(self, reset_positions: bool = True) -> None:
        self.game.grid.remove(self.ghost)
        self.ghost.hide()

        if reset_positions:
            self.ghost.x = -1
            self.ghost.y = -1

    def on_ghost_click(self, client, object: GameObject, *args) -> None:
        if client.ninja != self:
            return

        if self.client.is_ready:
            return

        self.hide_ghost()
        self.show_targets()

    def show_targets(self) -> None:
        self.remove_targets()

        healable_tiles = self.game.grid.healable_tiles(
            self.x if not self.placed_ghost else self.ghost.x,
            self.y if not self.placed_ghost else self.ghost.y,
            self
        )

        for tile in healable_tiles:
            tile_x = int(tile.x - 0.5)
            tile_y = int(tile.y - 0.9998)

            self.targets.append(target := Target(self, tile_x, tile_y))
            target.show_heal()

        attackable_tiles = self.game.grid.attackable_tiles(
            self.x if not self.placed_ghost else self.ghost.x,
            self.y if not self.placed_ghost else self.ghost.y,
            self
        )

        for tile in attackable_tiles:
            tile_x = int(tile.x - 0.5)
            tile_y = int(tile.y - 0.9998)

            self.targets.append(target := Target(self, tile_x, tile_y))
            target.show_attack()

    def hide_targets(self) -> None:
        for target in self.targets:
            target.hide()

    def remove_targets(self) -> None:
        for target in self.targets:
            target.remove_object()

        self.targets = []

class WaterNinja(Ninja):
    name: str = 'Water'
    max_hp: int = 40
    range: int = 1
    attack: int = 10
    move: int = 2

    assets = AssetCollection({
        Asset.from_name('waterninja_move_ghost'),
        Asset.from_name('waterninja_attack_anim'),
        Asset.from_name('waterninja_idle_anim'),
        Asset.from_name('waterninja_move_anim'),
        Asset.from_name('waterninja_hit_anim'),
        Asset.from_name('waterninja_kostart_anim'),
        Asset.from_name('waterninja_koloop_anim'),
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

    def attack_animation(self, x: int, y: int) -> None:
        if self.x > x:
            self.mirror_mode = MirrorMode.X

        self.animate_object(
            'waterninja_attack_anim',
            play_style='play_once',
            reset=True,
            callback=self.reset_sprite_settings
        )
        self.idle_animation()

class SnowNinja(Ninja):
    name: str = 'Snow'
    max_hp: int = 25
    range: int = 3
    attack: int = 6
    move: int = 3

    assets = AssetCollection({
        Asset.from_name('snowninja_move_ghost'),
        Asset.from_name('snowninja_idle_anim'),
        Asset.from_name('snowninja_attack_anim'),
        Asset.from_name('snowninja_heal_anim'),
        Asset.from_name('snowninja_hit_anim'),
        Asset.from_name('snowninja_kostart_anim'),
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
    max_hp: int = 30
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
