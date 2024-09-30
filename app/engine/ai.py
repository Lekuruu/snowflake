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
        self.logger.info(f'{self.element} {message}') # use 'info' for filtering these logs

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
            self.obj_within_range(ninja, 1)
        )

    def gain_stamina(self) -> None:
        self.power_card_stamina = min(self.power_card_stamina + 2.5, 10)
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
        if self.power_card_stamina >= 10:
            self.power_card_stamina = 0
            new_card = random.choice(self.owned_cards)
            self.send_message(f"cards owned {len(self.owned_cards)}")
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
            if self.selected_card and self.game.pending_cards >= random.choice([2, 3]):
                return True
        return False

    def obj_within_range(self, obj, query_range):
        return (
            obj != self.ninja and self.game.grid.distance_with_obstacles(
                (self.ninja.x, self.ninja.y), (obj.x, obj.y)
            ) <= query_range
        )       

    def ninjas_within_range(self) -> Iterator[Ninja]:
        return (
            ninja for ninja in self.game.ninjas
            if self.obj_within_range(ninja, self.ninja.move)
        )

    def do_strategy(self) -> tuple[int, int]:
        selection = None
        old_position = (self.ninja.x, self.ninja.y)
        ninja_coords = old_position
        enemies = list(self.game.enemies)
        last_distance = float('inf')

        desired_distance = {'water': 0, 'snow': 3, 'fire': 2}.get(self.element, 1)
        new_position, attack_coords, attacker_hp_prpn = None, None, None

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
                min_distance < last_distance # closer distance
            )
        
            # Skip if new position is no better or too close to enemies
            if not is_valid or min_distance < desired_distance or min_distance == last_distance:
                continue

            # Update the new position and attack coordinates
            new_position, attack_coords = position, (enemy_obj.x, enemy_obj.y)
            attacker_hp_prpn = int((100 * enemy_obj.hp) / enemy_obj.max_hp)
            last_distance = min_distance

        # Place the ghost ninja if a valid new position was found
        if new_position and new_position != old_position:
            self.ninja.place_ghost(*new_position)

        # Update selection for attack or card placement
        if last_distance <= self.ninja.move:
            selection = attack_coords
            
        max_damage = 0
        ninja_coords = None

        for ninja in self.ninjas_within_range():
            damage = ninja.max_hp - ninja.hp

            # Check if the current ninja has taken more damage than the current max_damage
            if max_damage < damage <= ninja.max_hp:

                max_damage = damage
                ninja_coords = (ninja.x, ninja.y)

                # Check if the ninja's damage reaches a threshold for healing
                percentage = int((damage * 100) / ninja.max_hp)
                threshold = 30 if self.element == "snow" else 50

                self.logger.info(f"{ninja.name} is {percentage}% damaged")

                if threshold <= percentage <= 100:

                    self.logger.info(f" -- {self.element} Meets the Damage Threshold %")

                    if not self.is_ninja_selected(ninja):

                        if not attack_coords or percentage > 85 or random.choice([True, False]):
                            selection = ninja_coords
                            self.send_message(f"{ninja.name} is healable!")

        if selection: 

            card_xy = None  

            if self.card_being_placed():
                self.send_message("has recieved a new card - resetting stamina")
                self.send_message(f"attacker is now {attacker_hp_prpn}% of max hp")
                if attacker_hp_prpn > 30:
                    card_xy = attack_coords                 
                if self.element == 'snow' and ninja_coords:
                    self.send_message("is eligible to place snow card")
                    card_xy = ninja_coords 

            if card_xy:
                self.selected_card.place(*card_xy)
                self.cards_queue.pop(0)
                self.send_message(f"placed card {self.selected_card.id}")
                self.send_message(f"queue == {[card.id for card in self.cards_queue]}")

            else:
                self.select_target(*selection)


    def unlock_stamp(self, id: int, session: Session | None = None) -> None:
        self.logger.info(f"{self.element} has unlocked the {random.choice(['Ancient Sensei', 'Epic Saga', 'Ninja Siesta'])} award")
        pass




