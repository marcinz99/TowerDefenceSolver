# BO 2021
# Authors: Łukasz Kita, Mateusz Pawłowicz, Michał Szczepaniak, Marcin Zięba
"""
Tower Defence Solver.

Candidate class.
"""
# Required for typing class inside itself
from __future__ import annotations

import copy
import numpy as np
from tower_defence_solver.utils import get_dmg_patch
from tower_defence_solver import TowerDefenceSolver, utils
from typing import List, Dict


class Candidate:
    def __init__(self, purchases: List[Dict], game: TowerDefenceSolver, time: int = 0) -> None:
        """
        Candidate instance.

        :param purchases:
        :param game:
        """
        self.game = game
        self.purchases = purchases
        self.time = time
        self.dmg_map = np.zeros((self.game.map_height, self.game.map_width))
        self.opponent_hp = np.zeros((self.game.map_height, self.game.map_width))
        self.gold = self.game.initial_gold
        self.base_hp = self.game.initial_hp

        self.initial_purchases = copy.deepcopy(purchases)

        self.delayed_purchases = []
        self.bought_purchases = []

    def __repr__(self) -> str:
        """
        Get string representation of the candidate.

        :return:
        """
        frame = "\n[CANDIDATE]\n\tTIME = {}, HP = {}, GOLD = {}".format(self.time, self.base_hp, self.gold)
        frame += "\n\nOPPONENT HP MAP:\n" + str(self.opponent_hp)
        frame += "\n\nTOWER DAMAGE MAP:\n" + str(self.dmg_map)
        frame += "\n\nPlanned purchases:\n\t" + str(self.initial_purchases) + "\n"

        unique_delays = self.get_unique_delays()
        frame += f"\nDelayed purchases ({len(unique_delays)}):\n"
        for purchase in unique_delays.values():
            frame += f"\tPurchase: {purchase[0]} -- final buy time: {purchase[1] + 1}\n"

        frame += f"\nBought towers ({len(self.bought_purchases)}):\n"
        for tower in self.bought_purchases:
            frame += f"\tTower: {tower}\n"

        return frame

    def swap_sim(self, candidates: List[Candidate]) -> None:
        """
        :param candidates: List of alive candidates
        :return: None
        """
        base_candidate = np.random.choice(candidates)
        while base_candidate == self:
            base_candidate = np.random.choice(candidates)

        self.purchases = copy.deepcopy(base_candidate.purchases)
        self.dmg_map = np.copy(base_candidate.dmg_map)
        self.opponent_hp = np.copy(base_candidate.opponent_hp)
        self.time = base_candidate.time
        self.gold = base_candidate.gold

        purchases_todo = [purchase for purchase in self.purchases if purchase["time"] >= self.time]
        for purchase in purchases_todo:
            modified_purchase = utils.get_random_purchase(self.game, self.purchases, self.time)
            # Randomly change tower type, position and maybe buy a bit later
            purchase["type"] = modified_purchase["type"]
            purchase["coords"] = modified_purchase["coords"]
            purchase["time"] = modified_purchase["time"]

        future_purchases = np.random.choice(3)
        for _ in range(future_purchases):
            self.purchases.append(utils.get_random_purchase(self.game, self.purchases, self.time))

        self.purchases = sorted(self.purchases, key=lambda x: x["time"])

    def refresh(self) -> None:
        """
        Refresh candidate to the state before simulation.

        :return:
        """
        self.purchases = copy.deepcopy(self.initial_purchases)
        self.dmg_map = np.zeros((self.game.map_height, self.game.map_width))
        self.opponent_hp = np.zeros((self.game.map_height, self.game.map_width))
        self.time = 0
        self.gold = self.game.initial_gold
        self.base_hp = self.game.initial_hp

        self.delayed_purchases = []
        self.bought_purchases = []

    def get_unique_delays(self):
        used_purchases_coords = {}
        for dp in self.delayed_purchases:
            unique = dp['coords'], dp['type']

            if unique not in used_purchases_coords:
                used_purchases_coords[unique] = dp.copy(), dp['time']
            else:
                used_purchases_coords[unique] = used_purchases_coords[unique][0], dp['time']

        return used_purchases_coords

    def simulate_step(self) -> None:
        """
        Simulate one step.

        :return:
        """
        # Apply damage to opponent units and obtain gold
        new_opponent_hp = np.maximum(self.opponent_hp - self.dmg_map, 0.0)
        self.gold += self.game.dmg_to_gold_factor * np.sum(self.opponent_hp - new_opponent_hp)
        self.opponent_hp = new_opponent_hp

        # Apply damage to your base and check if you are still alive
        self.base_hp -= self.opponent_hp[self.game.path[-1]]

        # Do purchases if possible, if not set those purchases for the next time
        while len(self.purchases) > 0 and self.purchases[0]["time"] == self.time:
            # print(self.game.tower_types, self.purchases)
            tower_cost = self.game.tower_types[self.purchases[0]["type"]]["cost"]
            if tower_cost <= self.gold:
                purchase = self.purchases.pop(0)
                utils.check_for_tower_rebuy(self.game, purchase, self.bought_purchases, self.dmg_map)
                self.gold -= tower_cost
                self.dmg_map += get_dmg_patch(self.game, purchase["coords"], purchase["type"])
                self.bought_purchases.append(purchase.copy())
            else:
                self.delayed_purchases.append(self.purchases[0].copy())
                self.purchases[0]["time"] += 1

        # Move opponent units forward
        for _, (coords_to, coords_from) in enumerate(self.game.move_generator):
            self.opponent_hp[coords_to] = self.opponent_hp[coords_from]
        self.opponent_hp[self.game.path[0]] = self.game.enemy_spawning_function(self.time)

        # Increment time
        self.time += 1
