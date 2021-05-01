import copy
import numpy as np
from tower_defence_solver.utils import get_dmg_patch


class Candidate:
    def __init__(self, purchases, game):
        self.game = game
        self.purchases = purchases
        self.time = 0
        self.dmg_map = np.zeros((self.game.map_height, self.game.map_width))
        self.opponent_hp = np.zeros((self.game.map_height, self.game.map_width))
        self.gold = self.game.initial_gold
        self.base_hp = self.game.initial_hp

        self.initial_purchases = copy.deepcopy(purchases)

    def __repr__(self):
        frame = "TIME = {}, HP = {}, GOLD = {}".format(self.time, self.base_hp, self.gold)
        frame += '\n' + str(self.opponent_hp)
        frame += '\n' + str(self.dmg_map)
        frame += '\n' + str(self.initial_purchases) + '\n'
        return frame

    def refresh(self):
        self.purchases = copy.deepcopy(self.initial_purchases)
        self.dmg_map = np.zeros((self.game.map_height, self.game.map_width))
        self.opponent_hp = np.zeros((self.game.map_height, self.game.map_width))
        self.time = 0
        self.gold = self.game.initial_gold
        self.base_hp = self.game.initial_hp

    def simulate_step(self):
        # Apply damage to opponent units and obtain gold
        new_opponent_hp = np.maximum(self.opponent_hp - self.dmg_map, 0.)
        self.gold += np.sum(self.opponent_hp - new_opponent_hp)
        self.opponent_hp = new_opponent_hp

        # Apply damage to your base and check if you are still alive
        self.base_hp -= self.opponent_hp[self.game.path[-1]]

        # Do purchases if possible, if not set those purchases for the next time
        while len(self.purchases) > 0 and self.purchases[0]['time'] == self.time:
            # print(self.game.tower_types, self.purchases)
            tower_cost = self.game.tower_types[self.purchases[0]['type']]['cost']
            if tower_cost <= self.gold:
                purchase = self.purchases.pop(0)
                self.gold -= tower_cost
                self.dmg_map += get_dmg_patch(self.game, purchase['coords'], purchase['type'])
            else:
                self.purchases[0]['time'] += 1

        # Move opponent units forward
        for _, (coords_to, coords_from) in enumerate(self.game.move_generator):
            self.opponent_hp[coords_to] = self.opponent_hp[coords_from]
        self.opponent_hp[self.game.path[0]] = self.time * 20

        # Increment time
        self.time += 1
