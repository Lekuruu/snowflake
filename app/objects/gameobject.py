
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from app.data.constants import OriginMode, MirrorMode
from .collections import SoundCollection, AssetCollection
from .asset import Asset
from .sound import Sound

if TYPE_CHECKING:
    from app.engine.penguin import Penguin
    from app.engine.game import Game

class GameObject:
    def __init__(
        self,
        game: "Game",
        name: str,
        x: int = 0,
        y: int = 0,
        assets=AssetCollection(),
        sounds=SoundCollection(),
        on_click: Callable | None = None,
        grid: bool = False
    ) -> None:
        self.game = game
        self.name = name
        self.id = -1
        self.x = x
        self.y = y
        self.assets = assets
        self.sounds = sounds
        self.game.objects.add(self)
        self.on_click = on_click
        self.grid = grid

        # Set default target
        self.target = self.game

        # Place object in grid
        if grid: self.game.grid[x, y] = self

        self._origin_mode = OriginMode.NONE
        self._mirror_mode = MirrorMode.NONE

    def __eq__(self, other: object) -> bool:
        if not getattr(other, 'id', None):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def origin_mode(self) -> OriginMode:
        return self._origin_mode

    @origin_mode.setter
    def origin_mode(self, value: OriginMode) -> None:
        self._origin_mode = value
        self.sprite_settings(
            origin_mode=self._origin_mode,
            mirror_mode=self._mirror_mode
        )

    @property
    def mirror_mode(self) -> MirrorMode:
        return self._mirror_mode

    @mirror_mode.setter
    def mirror_mode(self, value: MirrorMode) -> None:
        self._mirror_mode = value
        self.sprite_settings(
            origin_mode=self._origin_mode,
            mirror_mode=self._mirror_mode
        )

    @classmethod
    def from_asset(
        cls,
        name: str | list,
        game: "Game",
        x: int = 0,
        y: int = 0,
        grid: bool = False,
        on_click: Callable | None = None
    ) -> "GameObject":
        if isinstance(name, list):
            assets = AssetCollection([Asset.from_name(n) for n in name])
        else:
            assets = AssetCollection([Asset.from_name(name)])

        return GameObject(
            game,
            name,
            x,
            y,
            assets,
            grid=grid,
            on_click=on_click
        )

    def place_object(self) -> None:
        x = self.x
        y = self.y

        if self.grid:
            x = self.x + 0.5
            y = self.y + 1

        self.target.send_tag(
            'O_HERE',
            self.id,
            '0:1',  # TODO
            x,
            y,
            0,      # TODO
            1,      # TODO
            0,      # TODO
            0,      # TODO
            0,      # TODO
            self.name,
            '0:1',  # TODO
            0,      # TODO
            1,      # TODO
            0       # TODO
        )

    def move_object(self, x: int, y: int, duration: int = 600) -> None:
        self.x = x
        self.y = y

        if self.grid:
            self.game.grid.move(self, x, y)
            x = x + 0.5
            y = y + 1

        self.target.send_tag(
            'O_SLIDE',
            self.id,
            x,
            y,
            128, # Z Coordinate
            duration
        )

    def remove_object(self) -> None:
        self.target.send_tag('O_GONE', self.id)
        self.game.objects.remove(self)
        self.game.grid.remove(self)
        self.remove_pending_animations()

    def remove_pending_animations(self) -> None:
        try:
            self.game.callbacks.pending_animations.pop(self.id)
        except KeyError:
            pass

    def animate_object(
        self,
        name: str,
        play_style: str = 'play_once',
        duration: int | None = None,
        time_scale: int = 1,
        reset: bool = False,
        register: bool = True,
        callback: Callable | None = None
    ) -> None:
        asset = self.assets.by_name(name)
        handle_id = -1

        if register:
            handle_id = self.game.callbacks.register_animation(
                self.id,
                callback
            )

        self.target.send_tag(
            'O_ANIM',
            self.id,
            f'0:{asset.index}',
            play_style,
            duration or '',
            time_scale,
            int(not reset),
            self.id,
            handle_id
        )

    def place_sprite(self, name: str, target: "Penguin" | None = None) -> None:
        asset = self.assets.by_name(name)
        target = target or self.target

        target.send_tag(
            'O_SPRITE',
            self.id,
            f'0:{asset.index}',
            0, # TODO
            '' # TODO
        )

    def load_sprite(self, name: str) -> None:
        asset = self.assets.by_name(name)

        self.target.send_tag(
            'S_LOADSPRITE',
            f'0:{asset.index}'
        )

    def load_sprites(self) -> None:
        for asset in self.assets:
            self.target.send_tag(
                'S_LOADSPRITE',
                f'0:{asset.index}'
            )

    def animate_sprite(
        self,
        start_frame: int = 0,
        end_frame: int = 0,
        backwards: bool = False,
        play_style = 'play_once',
        duration: int = 50,
    ) -> None:
        self.target.send_tag(
            'O_SPRITEANIM',
            self.id,
            start_frame + 1,
            end_frame + 1,
            int(backwards),
            play_style,
            duration
        )

    def sprite_settings(
        self,
        scale_x: int = 1,
        scale_y: int = 1,
        origin_mode: OriginMode = OriginMode.NONE,
        mirror_mode: MirrorMode = MirrorMode.NONE
    ) -> None:
        """This will update the sprite settings"""
        self.target.send_tag(
            'O_SPRITESETTINGS',
            self.id,
            'none', # Sprite layers
            scale_x,
            scale_y,
            '',
            '',
            '',
            origin_mode.value,
            mirror_mode.value
        )

        self._mirror_mode = mirror_mode
        self._origin_mode = origin_mode

    def reset_sprite_settings(self, *args) -> None:
        self.sprite_settings(
            scale_x=1,
            scale_y=1,
            origin_mode=OriginMode.NONE,
            mirror_mode=MirrorMode.NONE
        )
        self._mirror_mode = MirrorMode.NONE
        self._origin_mode = OriginMode.NONE

    def hide(self) -> None:
        if not self.assets.by_name('blank_png'):
            self.assets.add(Asset.from_name('blank_png'))

        self.place_sprite('blank_png')
        self.remove_pending_animations()

    def add_sound(
        self,
        name: str,
        looping: bool = False,
        volume: int = 100,
        radius: int = 0
    ) -> None:
        self.sounds.add(
            Sound.from_name(
                name,
                looping,
                volume,
                radius,
                self.id,
                self.id # TODO: Different id for response object?
            )
        )

    def play_sound(self, sound_name: str, target: "Penguin" | None = None) -> None:
        sound = self.sounds.by_name(sound_name)
        sound.play(target or self.game)

class LocalGameObject(GameObject):
    def __init__(
        self,
        game: "Game",
        client: "Penguin",
        name: str,
        x: int = 0,
        y: int = 0,
        assets=AssetCollection(),
        sounds=SoundCollection(),
        on_click: Callable | None = None
    ) -> None:
        super().__init__(
            game,
            name,
            x,
            y,
            assets,
            sounds,
            on_click
        )
        self.target = client
        self.client = client
