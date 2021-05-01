import unittest
import numpy as np
from tower_defence_solver import TowerDefenceSolver


class TestTDSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def test_general(self):
        path = [(1, 6), (1, 5), (1, 4), (1, 3), (1, 2), (1, 1), (1, 0)]
        tower_types = {
            0: {'dmg': 5 * np.ones((3, 3)), 'cost': 200},
            1: {'dmg': 15 * np.ones((3, 3)), 'cost': 200},
            2: {'dmg': 75 * np.ones((3, 3)), 'cost': 300}
        }

        def spawn(x):
            return 4 * x

        game = TowerDefenceSolver(
            map_width=7,
            map_height=3,
            path=path,
            tower_types=tower_types,
            enemy_spawning_function=spawn,
            initial_hp=100,
            initial_gold=1000
        )
        game.solve()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
