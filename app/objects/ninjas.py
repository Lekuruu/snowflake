
from __future__ import annotations

from typing import TYPE_CHECKING, List
from twisted.internet import reactor

if TYPE_CHECKING:
    from app.engine.penguin import Penguin
    from app.objects.enemies import Enemy
    from app.engine.game import Game

from app.data import MirrorMode, Phase
from app.objects.target import Target
from app.objects.effects import (
    SnowProjectile,
    FireProjectile,
    HealParticles
)
from app.objects import (
    SoundCollection,
    AssetCollection,
    GameObject,
    Sound,
    Asset
)

import time

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
        client: "Penguin",
        x: int = -1,
        y: int = -1
    ) -> None:
        super().__init__(
            client.game,
            self.__class__.name,
            x, y,
            grid=True,
            x_offset=0.5,
            y_offset=1
        )
        self.assets = self.__class__.assets
        self.sounds = self.__class__.sounds
        self.attack = self.__class__.attack
        self.range = self.__class__.range
        self.max_hp = self.__class__.max_hp
        self.hp = self.__class__.max_hp
        self.client = client

        self.targets: List["Target"] = []
        self.initialize_objects()

    @property
    def selected_target(self) -> "Target" | None:
        return next((target for target in self.targets if target.selected), None)

    @property
    def selected_object(self) -> GameObject | None:
        return self.selected_target.object if self.selected_target else None

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
            on_click=self.on_ghost_click,
            x_offset=0.5,
            y_offset=1
        )
        self.ghost.add_sound('sfx_mg_2013_cjsnow_uiselecttile')

        self.health_bar = GameObject.from_asset(
            'reghealthbar_animation',
            self.game,
            x=self.x,
            y=self.y,
            x_offset=0.5,
            y_offset=1
        )

    def remove_object(self) -> None:
        self.health_bar.remove_object()
        self.ghost.remove_object()
        super().remove_object()

    def move_object(self, x: int, y: int) -> None:
        self.health_bar.move_object(x, y, self.move_duration)
        super().move_object(x, y, self.move_duration)
        self.ghost.x = x
        self.ghost.y = y

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
        hp = max(0, min(hp, self.max_hp))
        self.animate_healthbar(self.hp, hp, duration=500)

        if hp <= 0:
            self.ko_animation()
            self.hp = hp

            if not self.client.disconnected:
                self.client.was_ko = True
                self.ko_sound()
            return

        if hp < self.hp:
            self.hit_animation()
        else:
            self.revive_animation()

        self.hp = hp

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
            self.targets.append(target := Target(self, tile.x, tile.y))
            target.show_heal()

        attackable_tiles = self.game.grid.attackable_tiles(
            self.x if not self.placed_ghost else self.ghost.x,
            self.y if not self.placed_ghost else self.ghost.y,
            self
        )

        for tile in attackable_tiles:
            self.targets.append(target := Target(self, tile.x, tile.y))
            target.show_attack()

    def hide_targets(self) -> None:
        for target in self.targets:
            target.hide()

    def remove_targets(self) -> None:
        for target in self.targets:
            target.remove_object()

        self.targets = []

    def attack_target(self, target: "Enemy"):
        # This delay seems to fix the mirror mode?
        time.sleep(0.25)

        self.attack_animation(target.x, target.y)
        target.set_health(target.hp - self.attack)

    def heal_target(self, target: "Ninja"):
        if self.client.last_tip == Phase.HEAL:
            self.game.hide_tip(self.client)

        if target.hp <= 0:
            self.revive_other_animation()
            return

        if self.name != 'Snow':
            return

        self.heal_animation()
        time.sleep(0.4)
        target.set_health(target.hp + self.attack)

    def idle_animation(self) -> None:
        ...

    def move_animation(self) -> None:
        ...

    def ko_animation(self) -> None:
        ...

    def attack_animation(self, x: int, y: int) -> None:
        ...

    def win_animation(self) -> None:
        ...

    def hit_animation(self) -> None:
        ...

    def heal_animation(self) -> None:
        ...

    def revive_animation(self) -> None:
        ...

    def revive_other_animation(self) -> None:
        ...

    def ko_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_penguinground')

    def move_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_footsteppenguin')

    def attack_sound(self) -> None:
        ...

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

    def idle_animation(self) -> None:
        self.animate_object(
            'waterninja_idle_anim',
            play_style='loop',
            register=False
        )

    def move_animation(self) -> None:
        self.animate_object(
            'waterninja_move_anim',
            play_style='play_once'
        )
        self.idle_animation()

    def ko_animation(self) -> None:
        self.animate_object(
            'waterninja_kostart_anim',
            play_style='play_once'
        )
        self.animate_object(
            'waterninja_koloop_anim',
            play_style='loop'
        )

    def hit_animation(self) -> None:
        self.animate_object(
            'waterninja_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def attack_animation(self, x: int, y: int) -> None:
        if self.x > x:
            self.mirror_mode = MirrorMode.X

        self.animate_object(
            'waterninja_attack_anim',
            play_style='play_once',
            callback=self.reset_sprite_settings,
            reset=True
        )
        self.idle_animation()

        time.sleep(0.45)
        self.attack_sound()

    def win_animation(self) -> None:
        self.animate_object(
            'waterninja_celebrate_anim',
            play_style='loop'
        )

    def revive_animation(self) -> None:
        self.animate_object(
            f'waterninja_revived_anim',
            play_style='play_once'
        )
        self.idle_animation()
        HealParticles(self.game, self.x, self.y).play()

    def revive_other_animation(self) -> None:
        self.animate_object(
            'waterninja_revive_other_intro_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            'waterninja_revive_other_loop_anim',
            play_style='loop'
        )

    def attack_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attackwater')

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

    def idle_animation(self) -> None:
        self.animate_object(
            'snowninja_idle_anim',
            play_style='loop',
            register=False
        )

    def move_animation(self) -> None:
        self.animate_object(
            'snowninja_move_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def ko_animation(self) -> None:
        self.animate_object(
            'snowninja_kostart_anim',
            play_style='play_once'
        )
        self.animate_object(
            'snowninja_koloop_anim',
            play_style='loop'
        )

    def hit_animation(self) -> None:
        self.animate_object(
            'snowninja_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def attack_animation(self, x: int, y: int) -> None:
        if self.x > x:
            self.mirror_mode = MirrorMode.X

        self.attack_sound()
        self.animate_object(
            'snowninja_attack_anim',
            play_style='play_once',
            callback=self.reset_sprite_settings,
            reset=True
        )
        self.idle_animation()

        time.sleep(0.3)
        self.projectile_animation(x, y)

    def projectile_animation(self, x: int, y: int) -> None:
        # This is kinda jank lol
        projectile = SnowProjectile(self.game, self.x, self.y)
        projectile.play(x, y)
        time.sleep(0.2)
        projectile.remove_object()

        projectile = SnowProjectile(self.game, self.x, self.y)
        projectile.play(x, y)
        reactor.callLater(0.2, projectile.remove_object)

    def heal_animation(self) -> None:
        self.animate_object(
            'snowninja_heal_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def win_animation(self) -> None:
        self.animate_object(
            'snowninja_celebrate_anim',
            play_style='play_once',
            reset=True
        )

    def revive_animation(self) -> None:
        self.animate_object(
            'snowninja_revive_anim_',
            play_style='play_once'
        )
        self.idle_animation()
        HealParticles(self.game, self.x, self.y).play()

    def revive_other_animation(self) -> None:
        self.animate_object(
            'snowninja_reviveothersintro_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            'snowninja_reviveothersloop_anim',
            play_style='loop'
        )

    def attack_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attacksnow')

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

    def idle_animation(self) -> None:
        self.animate_object(
            'fireninja_idle_anim',
            play_style='loop',
            register=False
        )

    def move_animation(self) -> None:
        self.animate_object(
            'fireninja_move_anim',
            play_style='play_once'
        )
        self.idle_animation()

    def ko_animation(self) -> None:
        self.animate_object(
            'fireninja_kostart_anim',
            play_style='play_once'
        )
        self.animate_object(
            'fireninja_koloop_anim',
            play_style='loop'
        )

    def hit_animation(self) -> None:
        self.animate_object(
            'fireninja_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def attack_animation(self, x: int, y: int) -> None:
        if self.x > x:
            self.mirror_mode = MirrorMode.X

        self.attack_sound()
        self.animate_object(
            'fireninja_attack_anim',
            play_style='play_once',
            callback=self.reset_sprite_settings,
            reset=True
        )
        self.idle_animation()

        time.sleep(1.45)
        self.projectile_animation(x, y)

    def projectile_animation(self, x: int, y: int) -> None:
        projectile = FireProjectile(self.game, self.x, self.y)
        projectile.play(x, y)
        reactor.callLater(0.25, projectile.remove_object)

    def win_animation(self) -> None:
        self.animate_object(
            'fireninja_celebratestart_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            'fireninja_celebrateloop_anim',
            play_style='loop'
        )

    def revive_animation(self) -> None:
        self.animate_object(
            'fireninja_revived_anim',
            play_style='play_once'
        )
        self.idle_animation()
        HealParticles(self.game, self.x, self.y).play()

    def revive_other_animation(self) -> None:
        self.animate_object(
            'fireninja_reviveother_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            'fireninja_reviveotherloop_anim',
            play_style='loop'
        )

    def move_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_footsteppenguinfire')

    def attack_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attackfire')
