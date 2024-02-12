
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.objects.ninjas import Ninja
    from app.engine import Penguin

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

    @property
    def object(self) -> GameObject:
        return self.game.grid[self.x, self.y]

    def show_attack(self) -> None:
        if self.selected:
            return

        self.type = 'attack'
        self.place_object()
        self.animate_object('ui_target_red_attack_intro_anim', reset=True)
        self.animate_object('ui_target_red_attack_idle_anim', play_style='loop')
        self.play_sound('sfx_mg_2013_cjsnow_uitargetred', self.client)
        self.game.send_tip(TipPhase.ATTACK, self.client)

    def show_heal(self) -> None:
        if self.selected:
            return

        self.type = 'heal'
        self.place_object()
        self.animate_object('ui_target_white_heal_intro_anim', reset=True)
        self.animate_object('ui_target_white_heal_idle_anim', play_style='loop')
        self.play_sound('sfx_mg_2013_cjsnow_uitargetred', self.client)
        self.game.send_tip(TipPhase.HEAL, self.client)

    def select(self) -> None:
        if self.selected:
            self.deselect()
            return

        if self.ninja.selected_target:
            self.ninja.selected_target.deselect()

        if self.type == 'attack':
            self.animate_object('ui_target_green_attack_selected_intro_anim', reset=True)
            self.animate_object('ui_target_green_attack_selected_idle_anim', play_style='loop')

        elif self.type == 'heal':
            self.animate_object('ui_target_green_heal_selected_intro_anim', reset=True)
            self.animate_object('ui_target_green_heal_selected_idle_anim', play_style='loop')

        if self.client.last_tip in (TipPhase.ATTACK, TipPhase.HEAL):
            self.game.hide_tip(self.client)

        self.selected = True
        self.play_sound('sfx_mg_2013_cjsnow_uitargetselect', self.client)

    def deselect(self) -> None:
        self.selected = False
        if self.type == 'attack':
            self.animate_object('ui_target_red_attack_intro_anim', reset=True)
            self.animate_object('ui_target_red_attack_idle_anim', play_style='loop')
        elif self.type == 'heal':
            self.animate_object('ui_target_white_heal_intro_anim', reset=True)
            self.animate_object('ui_target_white_heal_idle_anim', play_style='loop')

    def on_click(self, client: "Penguin", object: GameObject, *args) -> None:
        if client.is_ready:
            return

        if not self.game.timer.running:
            return

        self.select()
