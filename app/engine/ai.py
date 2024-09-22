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
        self.powermetre = 0 # stamina
        self.cards_queue = []

    @delay(0.25, 1.5)
    def confirm_move(self) -> None:
        if self.is_ready:
            self.logger.info(f'{self.element} is already ready, skipping confirm_move.')
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
        for ninja in self.game.ninjas:
            if self.should_revive_ally(ninja):
                self.logger.info(f'{self.element} is reviving ally at position: ({ninja.x}, {ninja.y}).')
                self.select_target(ninja.x, ninja.y)
                break  
        else: # no break in loop / no allies to revive
            self.action_strategy()

        self.confirm_move() 

    def handle_knockout(self) -> None:
        if self.member_card:
            self.logger.info(f'{self.element} is using a member card to revive themselves.')
            self.member_card.place()

    def is_ninja_getting_revived(self, ninja: Ninja) -> bool:
        return any(ninja.selected_object == ninja for ninja in self.game.ninjas)

    def should_revive_ally(self, ninja: Ninja) -> bool:
        return (
            ninja.hp <= 0 and
            not ninja.client.member_card and
            not self.is_ninja_getting_revived(ninja) and
            self.can_heal_ninja(ninja)
        )

    def action_strategy(self) -> None:
        action_strategies = {
            'snow': self.snow_strategy,
            'water': self.water_strategy,
            'fire': self.fire_strategy
        }
        strategy = action_strategies[self.element]
        self.selection(strategy())

    def select_target(self, x: int, y: int) -> None:
        for target in self.ninja.targets: # enemies and allies appended to "targets" in "ninjas.py" "show_targets"
            if x == target.x and y == target.y:
                target.select()
                break

    def selection(self, position: tuple[int, int]) -> None:   
        self.powermetre = min(self.powermetre + random.randint(1, 3), 10)

        self.logger.info(f'{self.element} stamina {self.powermetre}')

        if self.game.grid[position] is None: # pass tuple to grid
            self.logger.info(f'{self.element} position >> : {position}')
            self.ninja.place_ghost(*position) # "hide ghosts" and "move ninjas" in "run_until_next_round"   
            
        elif self.is_placing_power_card(position): 
            return         

        else:
            self.select_target(*position)

    def is_placing_power_card(self, position : tuple[int, int]) -> bool:
        
        if self.cards_available:
            drawn_card = self.draw_card()

            if drawn_card:           
                self.selected_card = drawn_card

                if self.game.pending_cards >= 3:
                    self.selected_card.place(*position) 
                    self.logger.info(f'{self.element} placed card {drawn_card.id}')
                    self.cards_queue.pop(0)
                    self.logger.info(f'{self.element} queue == {[card.id for card in self.cards_queue]}')
                    return True      

            return False

    def draw_card(self):         
        new_card = None
        if self.powermetre == 10:
            self.powermetre = 0
            new_card = random.choice(self.cards_available)
            self.cards_queue.append(new_card)
            self.logger.info(f'{self.element} added card {new_card.id}')
            self.logger.info(f'{self.element} queue == {[card.id for card in self.cards_queue]}')
            self.logger.info(f'{self.element} stamina {self.powermetre}')
            self.game.pending_cards += 1
            self.logger.info(f'cards queued {self.game.pending_cards}')
            
        if len(self.cards_queue) >= 1:
            new_card = self.cards_queue[0]
        return new_card

    def water_strategy(self) -> tuple[int, int]:
        return self.ai_strategy() # range 1

    def fire_strategy(self) -> tuple[int, int]:
        return self.ai_strategy() # range 2

    def snow_strategy(self) -> tuple[int, int]:
        return self.ai_strategy() # healing | range 3

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

    def valid_moves(self) -> Iterator[tuple[int, int]]: # computes each value only when needed rather than all at once
        min_x, max_x, min_y, max_y = self.adjusted_move_range()
    
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                position = (x, y)
                ninja_position = (self.ninja.x, self.ninja.y)

                if self.game.grid[x, y] is not None: # unobstructed / empty cell
                    continue

                distance = self.game.grid.distance_with_obstacles(ninja_position, position)
                if distance > self.ninja.move: # distance within move range
                    continue

                yield position

    def can_heal_ninja(self, target: Ninja) -> bool:
        ninja_area = self.game.grid.surrounding_tiles(target.x, target.y)
        can_heal = any(self.game.grid.can_move_to_tile(self.ninja, tile.x, tile.y) for tile in ninja_area)
        # obstacles are ignored in healing
        return can_heal

    def ninja_is_healable(self):
        for ninja in self.game.ninjas:
            if ninja.hp < ninja.max_hp * 0.60 and ninja != self.ninja: 
                if self.can_heal_ninja(ninja):
                    return ninja
        return None

    def ai_strategy(self) -> tuple[int, int]:
        grid_selection = (self.ninja.x, self.ninja.y)

        enemies = list(self.game.enemies)

        injured_ninja = self.ninja_is_healable()
        if injured_ninja and self.element == self.game.healing_ninja:  # if a healable ninja is found
            self.logger.info(f'{self.element} healing: {injured_ninja.name}')
            return injured_ninja.x, injured_ninja.y

        closest_enemy_distance, closest_enemy = float('inf'), None
        previous_distance = float('inf')

        for position in self.valid_moves():

            better_position = False

            enemy_distance, enemy = min(
                [(self.game.grid.distance_with_obstacles(position, (enemy.x, enemy.y)), enemy) for enemy in enemies],
                key=lambda item: item[0]  # nearest enemy distance
            )

            if self.element == self.game.healing_ninja:
            
                allies_distance, injured_ninja = max(
                    [(self.game.grid.distance(position, (ninja.x, ninja.y)), ninja) for ninja in self.game.ninjas],
                    key=lambda item: item[0]  
                )  # furthest ally distance

                if allies_distance < enemy_distance: 
                    previous_distance = allies_distance  
                    better_position = True

            else:
                if enemy_distance < previous_distance:
                    previous_distance = enemy_distance
                    better_position = True

            if better_position:
                grid_selection = position
                closest_enemy_distance, closest_enemy = enemy_distance, enemy

            if self.game.debugging:   
                tile = self.game.grid.get_tile(*grid_selection) 
                tile.place_sprite(f"ui_card_{self.element}", self) # client

        if closest_enemy_distance <= self.ninja.move:  # within range
            self.logger.info(f'{self.element} attacking: {closest_enemy.name}')
            return closest_enemy.x, closest_enemy.y  

        else:  # reposition if out of range
            return grid_selection

    def unlock_stamp(self, id) -> None:
        # bots have no stamps
        pass

