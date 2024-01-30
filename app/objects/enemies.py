
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
    move_duration: int = 600

    assets = AssetCollection()
    sounds = SoundCollection()

    def __init__(
        self,
        game: "Game",
        x: int = -1,
        y: int = -1
    ) -> None:
        super().__init__(game, self.__class__.name, x, y, grid=True, x_offset=0.5, y_offset=1)
        self.assets = self.__class__.assets
        self.sounds = self.__class__.sounds
        self.attack = self.__class__.attack
        self.range = self.__class__.range
        self.max_hp = self.__class__.max_hp
        self.hp = self.max_hp
        self.initialize_objects()

    def initialize_objects(self) -> None:
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
        super().remove_object()

    def spawn(self) -> None:
        self.spawn_animation()
        self.idle_animation()

    def move_object(self, x: int, y: int) -> None:
        self.health_bar.move_object(x, y, self.move_duration)
        super().move_object(x, y, self.move_duration)

    def place_healthbar(self) -> None:
        self.health_bar.x = self.x
        self.health_bar.y = self.y
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
        self.hp = hp

        if self.hp <= 0:
            self.ko_animation()
            self.game.wait_for_animations()
            self.remove_object()
        else:
            self.hit_animation()

    def spawn_animation(self) -> None:
        self.animate_object(
            f'snowman_spawn_anim',
            play_style='play_once',
            reset=True
        )
        self.spawn_sound()

    def idle_animation(self) -> None:
        ...

    def ko_animation(self) -> None:
        ...

    def hit_animation(self) -> None:
        ...

    def spawn_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmenappear')

    def ko_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmandeathexplode')

    def hit_sound(self) -> None:
        ...

class Sly(Enemy):
    name: str = 'Sly'
    max_hp: int = 30
    range: int = 3
    attack: int = 4
    move: int = 3
    move_duration: int = 1200

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
        Sound.from_name('sfx_mg_2013_cjsnow_snowmenappear'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmandeathexplode')
    })

    def idle_animation(self) -> None:
        self.animate_object(
            f'sly_idle_anim',
            play_style='loop',
            register=False
        )

    def ko_animation(self) -> None:
        self.animate_object(
            f'sly_ko_anim',
            play_style='play_once',
            reset=True
        )
        self.ko_sound()

    def hit_animation(self) -> None:
        self.animate_object(
            f'sly_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()
        self.hit_sound()

    def hit_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmanslyhit')

class Scrap(Enemy):
    name: str = 'Scrap'
    max_hp: int = 45
    range: int = 2
    attack: int = 5
    move: int = 2
    move_duration: int = 1200

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
        Sound.from_name('sfx_mg_2013_cjsnow_snowmenappear'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmandeathexplode')
    })

    def idle_animation(self) -> None:
        self.animate_object(
            f'scrap_idle_anim',
            play_style='loop',
            register=False
        )

    def ko_animation(self) -> None:
        self.animate_object(
            f'scrap_ko_anim',
            play_style='play_once',
            reset=True
        )
        self.ko_sound()

    def hit_animation(self) -> None:
        self.animate_object(
            f'scrap_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def hit_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmanscraphit')

class Tank(Enemy):
    name: str = 'Tank'
    max_hp: int = 60
    range: int = 1
    attack: int = 10
    move: int = 1
    move_duration: int = 1100

    assets = AssetCollection({
        Asset.from_name('tank_swipe_horiz_anim'),
        Asset.from_name('tank_swipe_vert_anim'),
        Asset.from_name('tank_idle_anim'),
        Asset.from_name('tank_attack_anim'),
        Asset.from_name('tank_hit_anim'),
        Asset.from_name('tank_move_anim'),
        Asset.from_name('tank_ko_anim'),
        Asset.from_name('tank_daze_anim'),
        Asset.from_name('snowman_spawn_anim')
    })
    sounds = SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_snowmantankhit'),
        Sound.from_name('sfx_mg_2013_cjsnow_footsteptank'),
        Sound.from_name('sfx_mg_2013_cjsnow_attacktank'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmenappear'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmandeathexplode')
    })

    def idle_animation(self) -> None:
        self.animate_object(
            f'tank_idle_anim',
            play_style='loop',
            register=False
        )

    def ko_animation(self) -> None:
        self.animate_object(
            f'tank_ko_anim',
            play_style='play_once',
            reset=True
        )
        self.ko_sound()

    def hit_animation(self) -> None:
        self.animate_object(
            f'tank_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def hit_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmantankhit')
