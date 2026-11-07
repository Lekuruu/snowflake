
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.objects.ninjas import Ninja
    from app.engine.penguin import Penguin

from app.objects.gameobject import LocalGameObject, GameObject
from app.data import TipPhase

class Target(LocalGameObject):
    def __init__(
        self,
        ninja: "Ninja",
        x: int = -1,
        y: int = -1
    ) -> None:
        super().__init__(
            ninja.client,
            'Target',
            x, y,
            on_click=self.on_click,
            x_offset=0.5,
            y_offset=1.05
        )
        self.selected = False
        self.type = 'attack'
        self.ninja = ninja
        self.tile: GameObject | None = self.game.grid.get_tile(x, y) 
        self.attack_intro_sprite = 'ui_target_red_attack_intro_anim'
        self.attack_idle_sprite = 'ui_target_red_attack_idle_anim'
        self.heal_intro_sprite = 'ui_target_white_heal_intro_anim'
        self.heal_idle_sprite = 'ui_target_white_heal_idle_anim'
        self.attack_selected_intro_sprite = 'ui_target_green_attack_selected_intro_anim'
        self.attack_selected_idle_sprite = 'ui_target_green_attack_selected_idle_anim'
        self.heal_selected_intro_sprite = 'ui_target_green_heal_selected_intro_anim'
        self.heal_selected_idle_sprite = 'ui_target_green_heal_selected_idle_anim'

    @property
    def object(self) -> GameObject:
        return self.game.grid[self.x, self.y]

    def show_attack(self) -> None:
        if self.selected:
            return

        # TODO: Should we show ui_tile_attack here?

        self.type = 'attack'
        self.place_object()
        self.animate_object(self.attack_intro_sprite, reset=True)
        self.animate_object(self.attack_idle_sprite, play_style='loop')
        self.play_sound('sfx_mg_2013_cjsnow_uitargetred', self.client)
        self.game.send_tip(TipPhase.ATTACK, self.client)

    def show_heal(self) -> None:
        if self.selected:
            return

        if self.tile:
            self.tile.place_sprite('ui_tile_heal', self.client)

        self.type = 'heal'
        self.place_object()
        self.animate_object(self.heal_intro_sprite, reset=True)
        self.animate_object(self.heal_idle_sprite, play_style='loop')
        self.play_sound('sfx_mg_2013_cjsnow_uitargetred', self.client)
        self.game.send_tip(TipPhase.HEAL, self.client)

    def select(self) -> None:
        if self.selected:
            self.deselect()
            return

        if self.ninja.selected_target:
            self.ninja.selected_target.deselect()

        if self.type == 'attack':
            self.animate_object(self.attack_selected_intro_sprite, reset=True)
            self.animate_object(self.attack_selected_idle_sprite, play_style='loop')
            self.play_sound('sfx_mg_2013_cjsnow_uitargetselect', self.client)

        elif self.type == 'heal':
            self.animate_object(self.heal_selected_intro_sprite, reset=True)
            self.animate_object(self.heal_selected_idle_sprite, play_style='loop')
            self.play_sound('sfx_mg_2013_cjsnow_uiselecttile', self.client)

        if self.client.last_tip in (TipPhase.ATTACK, TipPhase.HEAL):
            self.game.hide_tip(self.client)

        self.selected = True

    def deselect(self) -> None:
        self.selected = False
        if self.type == 'attack':
            self.animate_object(self.attack_intro_sprite, reset=True)
            self.animate_object(self.attack_idle_sprite, play_style='loop')
        elif self.type == 'heal':
            self.animate_object(self.heal_intro_sprite, reset=True)
            self.animate_object(self.heal_idle_sprite, play_style='loop')

    def on_click(self, client: "Penguin", object: GameObject, *args) -> None:
        if client.is_ready:
            return

        if not self.game.timer.running:
            return

        self.select()

    def remove_object(self) -> None:
        super().remove_object()

        if not self.tile:
            return

        if self.ninja.hp <= 0:
            self.tile.hide(self.client)
            return

        if self.tile not in self.ninja.ghost_tiles_in_range():
            self.tile.hide(self.client)
            return

        self.game.grid.update_tile_for_client(self.tile, self.client)

class TuskTarget(Target):
    def __init__(self, ninja: "Ninja", x: int = -1, y: int = -1) -> None:
        super().__init__(ninja, x, y)
        self.attack_intro_sprite = 'ui_target_red_attack_tusk_intro'
        self.attack_idle_sprite = 'ui_target_red_attack_idle_tusk_anim'
        self.attack_selected_intro_sprite = 'ui_target_green_attack_selected_intro_tusk_anim'
        self.attack_selected_idle_sprite = 'ui_target_green_idle_tusk'
