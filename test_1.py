import unittest
import numpy as np
from scipy.signal import convolve2d
from tower_defence_solver import TowerDefenceSolver


class TestTDSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def test_general(self):
        path = [(1, 6), (1, 5), (1, 4), (1, 3), (1, 2), (1, 1), (1, 0)]
        tower_types = {
            0: {'dmg': 5 * np.ones((3, 3)), 'cost': 200},
            1: {'dmg': 15 * np.ones((3, 3)), 'cost': 900},
            2: {'dmg': 40 * np.ones((3, 3)), 'cost': 3000},
            3: {'dmg': 10 * np.ones((5, 5)), 'cost': 800},
            4: {'dmg': 18 * np.ones((5, 5)), 'cost': 1800},
            5: {'dmg': 25 * np.ones((5, 5)), 'cost': 2500},
            6: {'dmg': 10 * (convolve2d(np.ones((5, 5)), np.ones((3, 3)), 'same') < 9), 'cost': 700},
            7: {'dmg': 20 * (convolve2d(np.ones((5, 5)), np.ones((3, 3)), 'same') < 9), 'cost': 1900},
            8: {'dmg': 35 * (convolve2d(np.ones((5, 5)), np.ones((3, 3)), 'same') < 9), 'cost': 4000},
            9: {'dmg': 15 * (convolve2d(np.ones((7, 7)), np.ones((3, 3)), 'same') < 9), 'cost': 2000},
            10: {'dmg': 25 * (convolve2d(np.ones((7, 7)), np.ones((3, 3)), 'same') < 9), 'cost': 4200},
            11: {'dmg': 40 * (convolve2d(np.ones((7, 7)), np.ones((3, 3)), 'same') < 9), 'cost': 6800}
        }

        # Functions defining enemy health
        def spawn1(x):
            return 20 * x

        def spawn2(x):
            return int(np.abs(10 * x + 20 * np.sin(x)))

        # Unpredictable functions
        def spawn3(x):
            return int(np.abs(np.random.normal(10*x, x/10)))

        def spawn4(x):
            return int(np.random.normal(15*x, 20))

        def spawn5(x):
            return int(np.sqrt(100*x))

        game = TowerDefenceSolver(
            map_width=7,
            map_height=3,
            path=path,
            tower_types=tower_types,
            enemy_spawning_function=spawn1,
            initial_hp=100,
            initial_gold=1000
        )
        game.solve(
            epochs=100,
            candidate_pool=100,
            premature_death_reincarnation=0,
            survivors_per_epoch=20
        )
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
