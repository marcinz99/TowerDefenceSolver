"""
Testing utility.
"""
import unittest
import numpy as np
from scipy.signal import convolve2d
from tower_defence_solver import TowerDefenceSolver
import enemy_health_functions as enemy


class TestTDSolver(unittest.TestCase):
    """
    Tower Defence TestCase.
    """
    @classmethod
    def setUpClass(cls):
        pass

    def test_general(self):
        """Basic usage test"""
        path = [(13, 13), (13, 12), (13, 11), (13, 10), (13, 9), (13, 8), (12, 8), (12, 7), (12, 6), (12, 5),
                (12, 4), (12, 3), (12, 2), (11, 2), (10, 2), (10, 3), (10, 4), (9, 4), (8, 4), (7, 4), (6, 4),
                (6, 5), (6, 6), (7, 6), (7, 7), (7, 8), (8, 8), (9, 8), (10, 8), (10, 9), (10, 10), (10, 11),
                (10, 12), (9, 12), (8, 12), (8, 11), (7, 11), (6, 11), (6, 12), (5, 12), (4, 12), (4, 11),
                (4, 10), (4, 9), (4, 8), (4, 7), (4, 6), (3, 6), (3, 5), (3, 4), (4, 4), (4, 3), (4, 2),
                (5, 2), (6, 2), (7, 2), (7, 1), (7, 0)]
        tower_types = {
            0: {"dmg": 5 * np.ones((3, 3)), "cost": 200},
            1: {"dmg": 15 * np.ones((3, 3)), "cost": 700},
            2: {"dmg": 40 * np.ones((3, 3)), "cost": 2000},
            3: {"dmg": 10 * np.ones((5, 5)), "cost": 500},
            4: {"dmg": 18 * np.ones((5, 5)), "cost": 1200},
            5: {"dmg": 25 * np.ones((5, 5)), "cost": 2000},
            6: {"dmg": 10 * (convolve2d(np.ones((5, 5)), np.ones((3, 3)), "same") < 9), "cost": 700},
            7: {"dmg": 20 * (convolve2d(np.ones((5, 5)), np.ones((3, 3)), "same") < 9), "cost": 1900},
            8: {"dmg": 35 * (convolve2d(np.ones((5, 5)), np.ones((3, 3)), "same") < 9), "cost": 4000},
            9: {"dmg": 15 * (convolve2d(np.ones((7, 7)), np.ones((3, 3)), "same") < 9), "cost": 2000},
            10: {"dmg": 25 * (convolve2d(np.ones((7, 7)), np.ones((3, 3)), "same") < 9), "cost": 4200},
            11: {"dmg": 40 * (convolve2d(np.ones((7, 7)), np.ones((3, 3)), "same") < 9), "cost": 6800},
        }

        game = TowerDefenceSolver(
            map_width=14,
            map_height=16,
            path=path,
            tower_types=tower_types,
            enemy_spawning_function=enemy.spawn1,
            initial_hp=100,
            initial_gold=2000,
            binary_op_prob=0.6,
            unary_ops_prob_distribution=[0.76, 0.05, 0.06, 0.06, 0.07],
            binary_ops_prob_distribution=None,
            dmg_to_gold_factor=0.2
        )
        solution, history = game.solve(
            epochs=20,
            candidate_pool=100,
            premature_death_reincarnation=3,
            survivors_per_epoch=20,
            weighted_by='time'
        )
        print(solution)

        np.save('generated/dmg_map_1', solution.dmg_map)
        with open('generated/history_1.txt', mode='a') as file:
            file.write(' '.join(history) + '\n')

        self.assertTrue(solution is not None)


if __name__ == "__main__":
    unittest.main()
