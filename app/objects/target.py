
from __future__ import annotations

from .collections import SoundCollection, AssetCollection
from .gameobject import LocalGameObject, GameObject
from .asset import Asset
from .sound import Sound

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.objects.ninjas import Ninja
    from app.engine import Penguin

class Target(LocalGameObject):
    assets = AssetCollection({
        Asset.from_name('ui_target_red_attack_intro_anim'),
        Asset.from_name('ui_target_red_attack_idle_anim'),
        Asset.from_name("ui_target_green_attack_selected_intro_anim"),
        Asset.from_name('ui_target_green_attack_selected_idle_anim'),
        Asset.from_name('ui_target_white_heal_intro_anim'),
        Asset.from_name('ui_target_white_heal_idle_anim'),
        Asset.from_name('ui_target_green_heal_selected_intro_anim'),
        Asset.from_name('ui_target_green_heal_selected_idle_anim')
    })
    sounds = SoundCollection({
       Sound.from_name('sfx_mg_2013_cjsnow_uitargetred'),
       Sound.from_name('sfx_mg_2013_cjsnow_uiselecttile')
    })

    def __init__(
        self,
        ninja: "Ninja",
        x: int = -1,
        y: int = -1
    ) -> None:
        super().__init__(ninja.game, ninja.client, 'Target', x, y, on_click=self.on_click)
        self.assets = self.__class__.assets
        self.sounds = self.__class__.sounds
        self.x += 0.5
        self.y += 1.05
        self.selected = False
        self.type = 'attack'
        self.ninja = ninja

    def show_attack(self) -> None:
        if self.selected:
            return

        self.type = 'attack'
        self.place_object()
        self.animate_object('ui_target_red_attack_intro_anim', reset=True)
        self.animate_object('ui_target_red_attack_idle_anim', play_style='loop')
        self.play_sound('sfx_mg_2013_cjsnow_uitargetred')

    def show_heal(self) -> None:
        if self.selected:
            return

        self.type = 'heal'
        self.place_object()
        self.animate_object('ui_target_white_heal_intro_anim', reset=True)
        self.animate_object('ui_target_white_heal_idle_anim', play_style='loop')
        self.play_sound('sfx_mg_2013_cjsnow_uitargetred')

    def select(self) -> None:
        if self.selected:
            self.deselect()
            return

        if self.ninja.selected_target:
            self.ninja.selected_target.deselect()

        self.selected = True
        if self.type == 'attack':
            self.animate_object('ui_target_green_attack_selected_intro_anim', reset=True)
            self.animate_object('ui_target_green_attack_selected_idle_anim', play_style='loop')
        elif self.type == 'heal':
            self.animate_object('ui_target_green_heal_selected_intro_anim', reset=True)
            self.animate_object('ui_target_green_heal_selected_idle_anim', play_style='loop')

        self.play_sound('sfx_mg_2013_cjsnow_uiselecttile')

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

        self.select()
