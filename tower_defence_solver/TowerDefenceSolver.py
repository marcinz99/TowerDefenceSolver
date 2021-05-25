# BO 2021
# Authors: Łukasz Kita, Mateusz Pawłowicz, Michał Szczepaniak, Marcin Zięba
"""
Tower Defence Solver.

This algorithm employs evolutionary approach to find as good solution as possible to the Tower Defence gameplay problem.
"""
import numpy as np
import copy
import tower_defence_solver.utils as utils
import tower_defence_solver.reproduction as reproduction
from tower_defence_solver.candidate import Candidate
from typing import List, Tuple, Dict, Callable, Optional


class TowerDefenceSolver:
    def __init__(
        self,
        map_width: int,
        map_height: int,
        path: List[Tuple[int, int]],
        tower_types: Dict[int, Dict],
        enemy_spawning_function: Callable,
        initial_hp: int,
        initial_gold: int,
        binary_op_prob: Optional[float] = None,
        unary_ops_prob_distribution: Optional[List[float]] = None,
        binary_ops_prob_distribution: Optional[List[float]] = None,
    ) -> None:
        """
        Main instance of the solver.

        :param map_width: Width of the map.
        :param map_height: Height of the map.
        :param path: Path from enemy base to player base.
        :param tower_types: Dictionary of available tower types.
        :param enemy_spawning_function: Function of time returning the amount of enemies spawned.
        :param initial_hp: Health points of the players base.
        :param initial_gold: Initial amount of money available for purchasing towers.
        :param binary_op_prob:
        :param unary_ops_prob_distribution:
        :param binary_ops_prob_distribution:
        """
        self.map_width = map_width
        self.map_height = map_height
        self.path = path
        self.tower_types = tower_types
        self.enemy_spawning_function = enemy_spawning_function
        self.initial_hp = initial_hp
        self.initial_gold = initial_gold
        self.p_binary = (
            np.array([1.0 - binary_op_prob, binary_op_prob]) if binary_op_prob is not None else binary_op_prob
        )
        self.p_unary_ops = (
            np.array(unary_ops_prob_distribution)
            if unary_ops_prob_distribution is not None
            else unary_ops_prob_distribution
        )
        self.p_binary_ops = (
            np.array(binary_ops_prob_distribution)
            if binary_ops_prob_distribution is not None
            else binary_ops_prob_distribution
        )

        self.move_generator = list(zip(self.path[::-1], self.path[-2::-1]))

    def __get_initial_population(self, n_candidates: int) -> List[List[Dict]]:
        """
        Function returning the candidates of initial population.

        :param n_candidates:
        :return:
        """
        population = []
        for _ in range(n_candidates):
            sample = []
            gold_for_sample = self.initial_gold
            possible_options = [item for item in self.tower_types.items() if item[1]["cost"] <= gold_for_sample]

            while possible_options:
                purchase_time = utils.get_random_purchase_time(0.3)
                tower_idx, tower = utils.choose_random_tower(possible_options)

                dmg_height, dmg_width = tower["dmg"].shape

                position = utils.get_random_position_near_path(
                    game=self,
                    cov_xx=dmg_width // 2,
                    cov_yy=dmg_height // 2,
                    purchased_towers=sample
                )

                gold_for_sample -= tower["cost"]
                possible_options = list(filter(lambda x: x[1]["cost"] <= gold_for_sample, self.tower_types.items()))
                sample.append(
                    {"time": purchase_time, "coords": position, "type": tower_idx},
                )

            sample = sorted(sample, key=lambda x: x["time"])
            population.append(sample)

        return population

    def solve(
        self,
        epochs: int = 100,
        candidate_pool: int = 100,
        premature_death_reincarnation: int = 0,
        survivors_per_epoch: int = 20,
    ) -> Optional[Candidate]:
        """
        Solve for best possible gameplay given provided parameters.

        :param epochs: Number of epochs to go through.
        :param candidate_pool: Number of candidates for each epoch.
        :param premature_death_reincarnation: Number of worst candidates to replace by mutation of still living one.
        :param survivors_per_epoch: Number of candidates to remain alive by the end of each epoch's simulation.
        :return:
        """
        initial_population = self.__get_initial_population(candidate_pool)
        highest_score = -1
        best_candidate = None

        candidates = [Candidate(purchases, self) for purchases in initial_population]
        n_must_die = candidate_pool + premature_death_reincarnation - survivors_per_epoch

        for i in range(epochs):
            left_to_add = premature_death_reincarnation

            n_dead = 0
            while n_dead < n_must_die:

                for candidate in candidates:
                    candidate.simulate_step()

                    if candidate.base_hp <= 0:
                        n_dead += 1
                        if n_dead >= n_must_die:
                            break

                        if left_to_add > 0:
                            candidate.swap_sim(candidates)
                            left_to_add -= 1
                        else:
                            candidates.remove(candidate)

            threshold_time = candidates[0].time
            candidates = reproduction.reproduction(self, candidates, n_must_die)

            for candidate in candidates:
                while True:
                    candidate.simulate_step()
                    if candidate.base_hp <= 0:
                        break

                if candidate.time > highest_score:
                    highest_score = candidate.time
                    best_candidate = copy.deepcopy(candidate)

                candidate.refresh()

            print("[{: 4}] Threshold time: {: 6}    |    All time high: {: 6}".format(i, threshold_time, highest_score))

        return best_candidate
