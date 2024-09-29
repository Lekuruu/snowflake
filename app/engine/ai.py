from __future__ import annotations

from typing import Callable, Iterator

from twisted.internet.address import IPv4Address
from twisted.internet import reactor

from app.engine.penguin import Penguin
from app.objects.ninjas import Ninja
from app.objects import GameObject
from app.data import penguins

import random

def delay(min: float, max: float) -> Callable:
    def decorator(func: Callable) -> Callable:
        return lambda *args, **kwargs: reactor.callLater(
            random.uniform(min, max),
            func, *args, **kwargs
        )
    return decorator

class PenguinAI(Penguin):
    def __init__(self, server, element: str, battle_mode: int) -> None:
        super().__init__(server, IPv4Address('TCP', '127.0.0.1', 69420))
        self.object = penguins.fetch_random()
        self.name = self.object.nickname
        self.element = element
        self.battle_mode = battle_mode
        self.pid = -1
        self.in_queue = True
        self.is_ready = True
        self.logged_in = True
        self.is_bot = True
        self.cards_queue = []

    def send_message(self, message: str) -> None:
        self.logger.info(f'{self.element} {message}')

    @delay(0.25, 1.5)
    def confirm_move(self) -> None:
        if self.is_ready:
            self.send_message("skipping confirm_move.")
            return
        confirm = GameObject(self.game, 'ui_confirm', x_offset=0.5, y_offset=1.05)
        confirm.x, confirm.y = self.ninja.x, self.ninja.y
        confirm.place_object()
        confirm.place_sprite(confirm.name)
        confirm.play_sound('SFX_MG_2013_CJSnow_UIPlayerReady_VBR8')
        self.is_ready = True

    @delay(0.5, 3)
    def select_move(self) -> None:
        if self.ninja.hp <= 0:
            self.handle_knockout()

        else:
            for ninja in self.game.ninjas:
                if self.should_revive_ally(ninja):
                    self.send_message(f"reviving ally at position: ({ninja.x}, {ninja.y})")
                    self.select_target(ninja.x, ninja.y)
                    break
            else:
                self.action_strategy()
        
        self.confirm_move() 

    def handle_knockout(self) -> None:
        if self.member_card:
            self.send_message("is using a member card for revival.")
            self.member_card.place()

    def is_ninja_selected(self, ninja: Ninja) -> bool:
        return any(ninja.selected_object == ninja for ninja in self.game.ninjas)

    def should_revive_ally(self, ninja: Ninja) -> bool:
        return (
            ninja.hp <= 0 and
            not ninja.client.member_card and
            not self.is_ninja_selected(ninja) and
            self.game.grid.distance_with_obstacles((self.ninja.x, self.ninja.y), (ninja.x, ninja.y)) == 1
        )

    def gain_stamina(self) -> None:
        self.power_card_stamina += 2
        self.send_message(f"stamina {self.power_card_stamina}")

    def action_strategy(self) -> None:
        self.do_strategy()
        self.gain_stamina()

    def select_target(self, x: int, y: int) -> None:
        for target in self.ninja.targets:  # enemies and allies appended to "targets" in "ninjas.py" "show_targets"
            if x == target.x and y == target.y:
                target.select()
                break  

    def adjusted_move_range(self) -> tuple[int, int, int, int]:
        # constrain moving range within the grid boundaries
        min_grid_x, max_grid_x, min_grid_y, max_grid_y = self.game.grid.grid_range
        ninja_x, ninja_y, move_range = self.ninja.x, self.ninja.y, self.ninja.move
        return (
            max(min_grid_x, ninja_x - move_range),
            min(max_grid_x, ninja_x + move_range),
            max(min_grid_y, ninja_y - move_range),
            min(max_grid_y, ninja_y + move_range)
        )

    def valid_moves(self) -> list[tuple[int, int]]:  # Return a list of valid moves
        min_x, max_x, min_y, max_y = self.adjusted_move_range()
        valid_positions = []  # Initialize an empty list to store valid positions
    
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                position = (x, y)
                ninja_position = (self.ninja.x, self.ninja.y)

                if self.game.grid[x, y] is not None:  # Check if cell is obstructed
                    continue

                distance = self.game.grid.distance_with_obstacles(ninja_position, position)
                if distance > self.ninja.move:  # Check if the position is within move range
                    continue

                valid_positions.append(position)  # Append the valid position to the list

        return valid_positions  # Return the list of valid positions

    def drawn_card(self):
        if self.power_card_stamina == 10:
            self.power_card_stamina = 0
            new_card = random.choice(self.owned_cards)
            self.cards_queue.append(new_card)
            self.send_message(f"added card {new_card.id}")
            self.send_message(f"queue == {[card.id for card in self.cards_queue]}")
            self.send_message(f"stamina {self.power_card_stamina}")
            self.game.pending_cards += 1
            self.send_message(f"game pending {self.game.pending_cards}")
            
        return self.cards_queue[0] if self.cards_queue else None

    def card_being_placed(self) -> bool:
        if self.owned_cards:
            self.selected_card = self.drawn_card()
            if self.selected_card and self.game.pending_cards >= 3:
                return True
        return False

    def within_range(self, ninja: Ninja) -> bool:
        ninja_area = self.game.grid.surrounding_tiles(ninja.x, ninja.y)
        return any(self.game.grid.can_move_to_tile(self.ninja, tile.x, tile.y) for tile in ninja_area)

    def ninjas_within_range(self)  -> Iterator[Ninja]:
        for ninja in self.game.ninjas:
            if ninja != self.ninja:
                if self.within_range(ninja):
                    yield ninja
        return None

    def do_strategy(self) -> tuple[int, int]:
        selection = None
        old_position = (self.ninja.x, self.ninja.y)
        ninja_coords = old_position
        enemies = list(self.game.enemies)
        old_distance = float('inf')

        desired_distance = self.ninja.move
        new_position, attack_coords = None, None

        # Iterate over valid positions
        for position in [old_position] + self.valid_moves():

            if self.element == "snow":
                distance_allies, _ = min(
                [(self.game.grid.distance(position, (ninja.x, ninja.y)), ninja) for ninja in self.game.ninjas],
                key=lambda item: item[0]
                )
                if distance_allies >= self.ninja.move:
                    continue  # Skip this position if too far from allies

            # Calculate the minimum distance to enemies
            min_distance, enemy_obj = min(
                [(self.game.grid.distance_with_obstacles(position, (enemy.x, enemy.y)), enemy) for enemy in enemies],
                key=lambda item: item[0]
            )

            is_valid = (
                position == old_position or  # initialize 
                min_distance == desired_distance or # maintain distance
                min_distance < old_distance # closer distance
            )
        
            # Skip if new position is no better or too close to enemies
            if not is_valid or min_distance < desired_distance or min_distance == old_distance:
                continue

            # Update the new position and attack coordinates
            new_position, attack_coords = position, (enemy_obj.x, enemy_obj.y)
            old_distance = min_distance

        # Place the ghost ninja if a valid new position was found
        if new_position and new_position != old_position:
            self.ninja.place_ghost(*new_position)

        # Update selection for attack or card placement
        if old_distance <= self.ninja.move:
            selection = attack_coords
            
        previous_hp = 100
        ninja_coords = None

        for ninja in self.ninjas_within_range():

            if ninja.hp < previous_hp:
                previous_hp = ninja.hp
                ninja_coords = (ninja.x, ninja.y)

            if 0 < ninja.hp < ninja.max_hp * (0.70 if self.element == "snow" else 0.50) and not self.is_ninja_selected(ninja):
                selection = (ninja.x, ninja.y)

        if selection:
            if self.card_being_placed():
                selection = ninja_coords if (self.element == 'snow' and ninja_coords) else attack_coords or selection
                self.selected_card.place(*selection)
                self.cards_queue.pop(0)
                self.send_message(f"placed card {self.selected_card.id}")
                self.send_message(f"queue == {[card.id for card in self.cards_queue]}")
            else:
                self.select_target(*selection)




