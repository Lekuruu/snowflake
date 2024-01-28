
from .collections import SoundCollection, AssetCollection
from .gameobject import GameObject
from .asset import Asset

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ninjas import Ninja

class Target(GameObject):
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
        'sfx_mg_2013_cjsnow_uitargetred',
        'sfx_mg_2013_cjsnow_uiselecttile'
    })

    def __init__(
        self,
        ninja: "Ninja",
        x: int = -1,
        y: int = -1
    ) -> None:
        super().__init__(ninja.game, 'Target', x, y, grid=False)
        self.assets = self.__class__.assets
        self.sounds = self.__class__.sounds
        self.x += 0.5
        self.y += 1.05
        self.selected = False
        self.type = 'attack'
        self.ninja = ninja
        self.on_click = self.select

    def show_attack(self) -> None:
        self.type = 'attack'
        self.place_object()
        self.animate_object('ui_target_red_attack_intro_anim', reset=True)
        self.animate_object('ui_target_red_attack_idle_anim', play_style='loop')

    def show_heal(self) -> None:
        self.type = 'heal'
        self.place_object()
        self.animate_object('ui_target_white_heal_intro_anim', reset=True)
        self.animate_object('ui_target_white_heal_idle_anim', play_style='loop')

    def select(self, *args) -> None:
        if self == self.ninja.selected_target:
            self.deselect()
            return

        if self.ninja.selected_target:
            self.ninja.selected_target.deselect()

        self.selected = True
        if self.type == 'attack':
            self.animate_object('ui_target_green_attack_selected_intro_anim', reset=True)
            self.animate_object('ui_target_green_attack_selected_idle_anim', play_style='loop')
        elif self.type == 'heal':
            self.animate_object('ui_target_green_heal_selected_intro_anim')
            self.animate_object('ui_target_green_heal_selected_idle_anim', play_style='loop')

    def deselect(self) -> None:
        self.selected = False
        if self.type == 'attack':
            self.animate_object('ui_target_red_attack_intro_anim', reset=True)
            self.animate_object('ui_target_red_attack_idle_anim', play_style='loop')
        elif self.type == 'heal':
            self.animate_object('ui_target_white_heal_intro_anim')
            self.animate_object('ui_target_white_heal_idle_anim', play_style='loop')
