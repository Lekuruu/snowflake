
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from app.engine.penguin import Penguin
    from app.engine.game import Game

from app.engine.callbacks import ActionType
from app.data.constants import OriginMode, MirrorMode
from .collections import SoundCollection, AssetCollection
from .asset import Asset
from .sound import Sound

class GameObject:
    """
    This class represents a game object. It is the base class for all objects in the game, such as ninjas and enemies.
    The protocol allows for placing, moving and animating the object, as well as playing sounds.
    """

    def __init__(
        self,
        game: "Game",
        name: str,
        x: int = 0,
        y: int = 0,
        assets=AssetCollection(),
        sounds=SoundCollection(),
        on_click: Callable | None = None,
        grid: bool = False,
        x_offset: int = 0,
        y_offset: int = 0,
        origin_mode: OriginMode = OriginMode.NONE,
        mirror_mode: MirrorMode = MirrorMode.NONE,
        x_scale: int = 1,
        y_scale: int = 1
    ) -> None:
        self.game = game
        self.name = name
        self.id = -1
        self.x = x
        self.y = y
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.assets = assets
        self.sounds = sounds
        self.game.objects.add(self)
        self.on_click = on_click
        self.grid = grid

        # Set default target
        self.target = self.game

        # Place object in grid
        if grid: self.game.grid[x, y] = self

        self._origin_mode = origin_mode
        self._mirror_mode = mirror_mode
        self._x_scale = x_scale
        self._y_scale = y_scale

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
        self.sprite_settings(
            self._x_scale,
            self._y_scale,
            origin_mode=value,
            mirror_mode=self._mirror_mode
        )

    @property
    def mirror_mode(self) -> MirrorMode:
        return self._mirror_mode

    @mirror_mode.setter
    def mirror_mode(self, value: MirrorMode) -> None:
        self.sprite_settings(
            self._x_scale,
            self._y_scale,
            origin_mode=self._origin_mode,
            mirror_mode=value
        )

    @property
    def x_scale(self) -> int:
        return self._x_scale

    @x_scale.setter
    def x_scale(self, value: int) -> None:
        self.sprite_settings(
            value,
            self._y_scale,
            origin_mode=self._origin_mode,
            mirror_mode=self._mirror_mode
        )

    @property
    def y_scale(self) -> int:
        return self._y_scale

    @y_scale.setter
    def y_scale(self, value: int) -> None:
        self.sprite_settings(
            self._x_scale,
            value,
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
        on_click: Callable | None = None,
        x_offset: int = 0,
        y_offset: int = 0,
        origin_mode: OriginMode = OriginMode.NONE,
        mirror_mode: MirrorMode = MirrorMode.NONE
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
            on_click=on_click,
            x_offset=x_offset,
            y_offset=y_offset,
            origin_mode=origin_mode,
            mirror_mode=mirror_mode
        )

    def place_object(self) -> None:
        x = self.x
        y = self.y

        self.target.send_tag(
            'O_HERE',
            self.id,
            '0:1',  # TODO
            x + self.x_offset,
            y + self.y_offset,
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

        if (
            self.origin_mode != OriginMode.NONE or
            self.mirror_mode != MirrorMode.NONE or
            self.x_scale != 1 or
            self.y_scale != 1
        ):
            self.sprite_settings(
                origin_mode=self.origin_mode,
                mirror_mode=self.mirror_mode,
                scale_x=self.x_scale,
                scale_y=self.y_scale
            )

    def move_object(self, x: int, y: int, duration: int = 600) -> None:
        self.x = x
        self.y = y

        if self.grid:
            self.game.grid.move(self, x, y)

        self.target.send_tag(
            'O_SLIDE',
            self.id,
            x + self.x_offset,
            y + self.y_offset,
            128, # Z Coordinate
            duration
        )

    def remove_object(self) -> None:
        self.target.send_tag('O_GONE', self.id)
        self.game.objects.remove(self)
        self.game.grid.remove(self)
        self.remove_pending_actions()

    def remove_pending_actions(self) -> None:
        self.game.callbacks.remove(self.id)

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

        if reset:
            self.remove_pending_actions()

        if register:
            handle_id = self.game.callbacks.register_action(
                name=name,
                type=ActionType.Animation,
                object_id=self.id,
                callback=callback
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
        self._x_scale = scale_x
        self._y_scale = scale_y

    def reset_sprite_settings(self, *args) -> None:
        if any([
            self._mirror_mode != MirrorMode.NONE,
            self._origin_mode != OriginMode.NONE,
            self._x_scale != 1,
            self._y_scale != 1
        ]):
            self.sprite_settings(
                scale_x=1,
                scale_y=1,
                origin_mode=OriginMode.NONE,
                mirror_mode=MirrorMode.NONE
            )
            self._mirror_mode = MirrorMode.NONE
            self._origin_mode = OriginMode.NONE
            self._x_scale = 1
            self._y_scale = 1

    def hide(self) -> None:
        if not self.assets.by_name('blank_png'):
            self.assets.add(Asset.from_name('blank_png'))

        self.place_sprite('blank_png')
        self.remove_pending_actions()

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

    def play_sound(self, sound_name: str, target: "Penguin" | None = None) -> Sound:
        sound = self.sounds.by_name(sound_name)
        sound.play(target or self.game, self.id)
        return sound

class LocalGameObject(GameObject):
    """
    This class is the same as `GameObject`, but is only visible to a single client.
    """

    def __init__(
        self,
        game: "Game",
        client: "Penguin",
        name: str,
        x: int = 0,
        y: int = 0,
        assets=AssetCollection(),
        sounds=SoundCollection(),
        on_click: Callable | None = None,
        x_offset: int = 0,
        y_offset: int = 0,
        origin_mode: OriginMode = OriginMode.NONE,
        mirror_mode: MirrorMode = MirrorMode.NONE,
        x_scale: int = 1,
        y_scale: int = 1
    ) -> None:
        super().__init__(
            game,
            name,
            x,
            y,
            assets,
            sounds,
            on_click,
            grid=False,
            x_offset=x_offset,
            y_offset=y_offset,
            origin_mode=origin_mode,
            mirror_mode=mirror_mode,
            x_scale=x_scale,
            y_scale=y_scale
        )
        self.target = client
        self.client = client
