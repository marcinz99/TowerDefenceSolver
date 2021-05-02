# BO 2021
# Authors: Łukasz Kita, Mateusz Pawłowicz, Michał Szczepaniak, Marcin Zięba
"""
Tower Defence Solver.

Utilities.
"""
import numpy as np
from tower_defence_solver import TowerDefenceSolver
from typing import List, Tuple, Dict, Optional


def get_random_purchase_time(
        p: float
) -> float:
    """
    For p=0.3 it varies from 0 to 10-15, maybe we should keep it always p=0.3
    and add parameter for starting time (so we can manipulate when the purchase
    occurs) - the result would be like: starting_time + np.random.geometric(p).

    :param p:
    :return:
    """
    return np.random.geometric(p)


def choose_random_tower(
        towers: List[Tuple[int, Dict]]
) -> Tuple[int, Dict]:
    return towers[np.random.choice(len(towers))]


def validate_pos(
        game: TowerDefenceSolver,
        position: Tuple[int, int],
        sample
) -> bool:
    if (
        position[0] < 0
        or position[1] < 0
        or position[0] >= game.map_height
        or position[1] >= game.map_width
        or position in game.path
    ):
        return False

    for purchase in sample:
        if purchase['coords'] == position:
            return False

    return True


def get_random_position_near_path(
        game: TowerDefenceSolver,
        cov_xx: int,
        cov_yy: int,
        purchased_towers: List[Dict],
        max_number_of_tries: Optional[int] = None
) -> Optional[Tuple[int, int]]:
    """
    May require to increase cov_x and cov_y as function retries to find free space
    or introduce max random attempts (because if whole map is filled with towers
    this function will attempt to find position for eternity)

    :param game:
    :param cov_xx:
    :param cov_yy:
    :param purchased_towers:
    :param max_number_of_tries:
    :return:
    """
    position = tuple(np.round(np.random.multivariate_normal(
        game.path[np.random.choice(len(game.path))],
        cov=[[cov_xx, 0], [0, cov_yy]])).astype(int)
    )

    number_of_tries = 0
    while not validate_pos(game, position, purchased_towers):
        position = tuple(
            np.round(
                np.random.multivariate_normal(
                    game.path[np.random.choice(len(game.path))],
                    cov=[[cov_xx, 0], [0, cov_yy]]
                )
            ).astype(int)
        )
        number_of_tries += 1
        if max_number_of_tries and number_of_tries > max_number_of_tries:
            return None

    return position


def get_dmg_patch(game, coords, tower_type):
    # Prepare damage adjustment to add
    patch = game.tower_types[tower_type]['dmg']
    additional_dmg = np.zeros((game.map_height, game.map_width))

    row, col = coords
    radius_row, radius_col = patch.shape[0] // 2, patch.shape[1] // 2

    for i in range(-radius_col, radius_col + 1):
        if not (0 <= col + i < game.map_width):
            continue

        for j in range(-radius_row, radius_row + 1):
            if not (0 <= row + j < game.map_height):
                continue

            additional_dmg[row + j, col + i] = patch[radius_col + i, radius_row + j]

    return additional_dmg
