"""
Testing utility.
"""
import unittest
import numpy as np
from scipy.signal import convolve2d
from tower_defence_solver import TowerDefenceSolver


# Functions defining enemy health
def spawn1(iteration: int) -> int:
    """Basic linear spawning function"""
    return 4 * iteration


def spawn2(iteration: int) -> int:
    """Custom spawning function"""
    return int(np.abs(10 * iteration + 20 * np.sin(iteration)))


# Non-deterministic functions
def spawn3(iteration: int) -> int:
    """Custom spawning function"""
    return int(np.abs(np.random.normal(10 * iteration, iteration / 10)))


def spawn4(iteration: int) -> int:
    """Custom spawning function"""
    return int(np.abs(np.random.normal(15 * iteration, 20)))


def spawn5(iteration: int) -> int:
    """Custom spawning function"""
    return int(np.sqrt(100 * iteration))


class TestTDSolver(unittest.TestCase):
    """
    Tower Defence TestCase.
    """
    @classmethod
    def setUpClass(cls):
        pass

    def test_general(self):
        """Basic usage test"""
        path = [(1, 8), (1, 7), (1, 6), (1, 5), (1, 4), (2, 4), (3, 4), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0)]
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
            map_width=9,
            map_height=8,
            path=path,
            tower_types=tower_types,
            enemy_spawning_function=spawn1,
            initial_hp=100,
            initial_gold=2000,
            binary_op_prob=0.4,
            unary_ops_prob_distribution=[0.8, 0.06, 0.07, 0.07],
            binary_ops_prob_distribution=None,
        )
        solution = game.solve(
            epochs=20,
            candidate_pool=100,
            premature_death_reincarnation=3,
            survivors_per_epoch=20,
            weighted_by='time'
        )
        print(solution)
        self.assertTrue(solution is not None)


if __name__ == "__main__":
    unittest.main()
