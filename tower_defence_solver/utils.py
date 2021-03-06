# BO 2021
# Authors: Łukasz Kita, Mateusz Pawłowicz, Michał Szczepaniak, Marcin Zięba
"""
Tower Defence Solver.

Utilities.
"""
import numpy as np
from tower_defence_solver import TowerDefenceSolver, utils
from typing import List, Tuple, Dict, Optional

Purchases = List[Dict]


def get_random_purchase_time(time: int) -> int:
    if np.random.rand() < 0.9:
        return int(np.random.uniform(0, time))
    else:
        return int(np.abs(np.random.standard_cauchy() * 0.2 * time) + time)


def get_random_initial_purchase_time(p: float) -> int:
    """
    For p=0.3 it varies from 0 to 10-15, maybe we should keep it always p=0.3
    and add parameter for starting time (so we can manipulate when the purchase
    occurs) - the result would be like: starting_time + np.random.geometric(p).

    :param p:
    :return:
    """
    return np.random.geometric(p)


def choose_random_tower(towers: List[Tuple[int, Dict]]) -> Tuple[int, Dict]:
    """
    Chooses random tower

    :param towers: list of towers
    :return: randomly chosen tower (with uniform distribution)
    """
    return towers[np.random.choice(len(towers))]


def validate_pos(game: TowerDefenceSolver, position: Tuple[int, int], purchases_list: Purchases) -> bool:
    """
    Checks if the given position is inside the map and is not occupied by some tower

    :param game: Instance of tower defence emulator
    :param position: tuple of indexes indicating the position on map
    :param purchases_list: list of purchases
    :return: True if the place is not occupied and is inside the map, False otherwise
    """
    if (
            position[0] < 0
            or position[1] < 0
            or position[0] >= game.map_height
            or position[1] >= game.map_width
            or position in game.path
    ):
        return False

    for purchase in purchases_list:
        if purchase["coords"] == position:
            return False

    return True


def get_random_position_near_path(
        game: TowerDefenceSolver,
        cov_xx: int,
        cov_yy: int,
        purchased_towers: Purchases,
        max_number_of_tries: Optional[int] = None,
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
    position = tuple(
        np.round(
            np.random.multivariate_normal(game.path[np.random.choice(len(game.path))], cov=[[cov_xx, 0], [0, cov_yy]])
        ).astype(int)
    )

    number_of_tries = 0
    while not validate_pos(game, position, purchased_towers):
        position = tuple(
            np.round(
                np.random.multivariate_normal(
                    game.path[np.random.choice(len(game.path))], cov=[[cov_xx, 0], [0, cov_yy]]
                )
            ).astype(int)
        )
        number_of_tries += 1
        if max_number_of_tries and number_of_tries > max_number_of_tries:
            return None

    return position


def get_dmg_patch(game: TowerDefenceSolver, coords: Tuple[int, int], tower_type: int) -> np.array:
    """
    Returns a 2D array of additional damage taken by a tower of given type, placed on a given position

    :param game: instance of tower defence emulator
    :param coords: position where the tower will be placed
    :param tower_type: integer indicating the tower type (order in game.tower_types list)
    :return: array describing the additional damage taken by a tower of the specified type placed on some coordinates
    """
    # Prepare damage adjustment to add
    patch = game.tower_types[tower_type]["dmg"]
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

    return additional_dmg / 2


def get_random_purchase(game: TowerDefenceSolver, purchases: Purchases, time: int) -> Dict:
    """
    :param game: instance of tower defence emulator
    :param purchases: list of towers planned to be bought
    :param time: earliest time possible of purchase
    :return:
    """
    # Random tower type, position and time in future base on variable 'time'
    purchase = {"type": np.random.choice(len(game.tower_types))}
    dmg_height, dmg_width = game.tower_types[purchase["type"]]["dmg"].shape
    purchase["coords"] = utils.get_random_position_near_path(
        game=game,
        cov_xx=dmg_width // 2,
        cov_yy=dmg_height // 2,
        purchased_towers=purchases
    )
    purchase["time"] = time + utils.get_random_purchase_time(0.3)
    return purchase


def find_tower_on_this_spot(spot: Tuple[int, int], bought_towers: Purchases):
    """
    :param spot: spot to check
    :param bought_towers: list of already done purchases
    :return:
    """
    for tower in bought_towers:
        if tower["coords"] == spot:
            return tower
    return None


def check_for_tower_rebuy(game: TowerDefenceSolver,
                          purchase: Dict,
                          bought_towers: Purchases,
                          dmg_patch: np.array):
    """
    :param game: instance of tower defence emulator
    :param purchase: purchase to check for rebuy
    :param bought_towers: list of already done purchases
    :param dmg_patch: array representing damage done by towers
    :return:
    """
    spot = purchase["coords"]
    prior_tower = find_tower_on_this_spot(spot, bought_towers)
    if prior_tower:
        # If there is a tower on the spot, we remove it so we can place a new tower
        dmg_patch -= get_dmg_patch(game, spot, prior_tower["type"])
