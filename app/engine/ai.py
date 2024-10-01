from __future__ import annotations

from typing import Callable, Iterator

from twisted.internet.address import IPv4Address
from twisted.internet import reactor
from sqlalchemy.orm import Session
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
        self.power_card_stamina = min(self.power_card_stamina + 3, 10)

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
            self.cards_queue.append(new_card)
            self.send_message(f"(drawn card) cards queued == {[card.id for card in self.cards_queue]}")
            self.game.pending_cards += 1
            
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
        old_position = (self.ninja.x, self.ninja.y)
        ninja_coords = old_position
        enemies = list(self.game.enemies)
        last_distance = float('inf')

        desired_distance = self.get_desired_distance()
        new_position, attack_coords, attack_name, attacker_health_loss_percent = None, None, None, None

        # Evaluate all valid positions including current one
        for position in [old_position] + self.valid_moves():
            if self.should_skip_position(position):
                continue

            # Get closest enemy and their distance
            min_distance, enemy_obj = self.get_closest_enemy(position, enemies)

            if not self.is_valid_position(position, min_distance, last_distance, desired_distance):
                continue

            if min_distance < desired_distance:
                continue

            # Update the new position and potential attack information
            new_position, attack_coords, attack_name, attacker_health_loss_percent = self.update_attack_position(
                position, enemy_obj, min_distance
            )
            last_distance = min_distance

        self.handle_ghost_placement(new_position, old_position)

        if self.game.enemies and self.game.enemies[0].name == "Tusk":
            last_distance -= 1  # Specific rule for enemy "Tusk"

        selection = self.determine_attack_or_heal(last_distance, attack_coords, attack_name)

        if not selection:
            return

        if not self.handle_card_placement(selection, ninja_coords, attack_coords, attacker_health_loss_percent):        
            self.select_target(*selection)


    def get_desired_distance(self) -> int:
        return {'water': 0, 'snow': 3, 'fire': 2}.get(self.element, 1)


    def should_skip_position(self, position: tuple[int, int]) -> bool:
        if self.element == "snow":
            closest_ally_distance = min(
                self.game.grid.distance(position, (ninja.x, ninja.y)) for ninja in self.game.ninjas
            )
            if closest_ally_distance > self.ninja.range:
                return True  # Too far from allies
        return False


    def get_closest_enemy(self, position: tuple[int, int], enemies: list) -> tuple[int, object]:
        return min(
            [(self.game.grid.distance_with_obstacles(position, (enemy.x, enemy.y)), enemy) for enemy in enemies],
            key=lambda item: item[0]
        )


    def is_valid_position(self, position: tuple[int, int], min_distance: int, last_distance: int, desired_distance: int) -> bool:
        return position == (self.ninja.x, self.ninja.y) or min_distance == desired_distance or min_distance < last_distance


    def update_attack_position(self, position: tuple[int, int], enemy_obj: object, min_distance: int) -> tuple:
        attack_coords = (enemy_obj.x, enemy_obj.y)
        attack_name = enemy_obj.name
        attacker_health_loss_percent = int((100 * enemy_obj.hp) / enemy_obj.max_hp)
        return position, attack_coords, attack_name, attacker_health_loss_percent


    def handle_ghost_placement(self, new_position: tuple[int, int], old_position: tuple[int, int]):
        if new_position and new_position != old_position:
            self.ninja.place_ghost(*new_position)


    def determine_attack_or_heal(self, last_distance: int, attack_coords: tuple[int, int], attack_name: str) -> tuple[int, int]:
        selection = None
        if last_distance <= self.ninja.range:
            selection = attack_coords
            self.send_message(f"is attacking {attack_name}")

        if self.element == 'snow':
            selection = self.check_healing(selection)
        
        return selection


    def check_healing(self, selection: tuple[int, int]) -> tuple[int, int]:
        max_loss, ninja_coords, adjusted_selection = 0, None, None
        for ninja in self.ninjas_within_range():
            health_loss = ninja.max_hp - ninja.hp
            if max_loss < health_loss <= ninja.max_hp:
                max_loss = health_loss
                ninja_coords = (ninja.x, ninja.y)
                health_lost_percent = int((health_loss * 100) / ninja.max_hp)
                self.logger.info(f"{ninja.name} is {health_lost_percent}% damaged")
                if 30 <= health_lost_percent < 100:
                    self.logger.info(f"-- {ninja.name} Meets the Damage Threshold for {self.element}")
                    if health_lost_percent > 70 or not selection or random.choice([True, True, False]):
                        selection = ninja_coords
                        if ninja.placed_ghost:
                            adjusted_selection = (ninja.ghost.x, ninja.ghost.y)
                        self.send_message(f"is healing {ninja.name}")
                    else:
                        self.send_message("chose not to heal")
                        
        return selection


    def handle_card_placement(self, selection: tuple[int, int], ninja_coords: tuple[int, int], attack_coords: tuple[int, int], attacker_health_loss_percent: int):

        card_xy = None
        if self.card_being_placed():
            if self.element == 'snow':
                if selection == ninja_coords:
                    self.send_message("is placing down a snow card")
                    card_xy = ninja_coords
            elif attacker_health_loss_percent > 30:
                self.send_message("attacker meets health requirements for card")
                card_xy = attack_coords

        if card_xy:
            self.selected_card.place(*card_xy)
            self.cards_queue.pop(0)
            self.send_message(f"(place card) -- cards queued == {[card.id for card in self.cards_queue]}")
            return True
            
        return False   
        

    def unlock_stamp(self, id: int, session: Session | None = None) -> None:
        pass




