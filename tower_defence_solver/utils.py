import numpy as np


def get_random_purchase_time(p):
    """
    For p=0.3 it varies from 0 to 10-15, maybe we should keep it always p=0.3
    and add parameter for starting time (so we can manipulate when the purchase
    occures) - the result would be like: starting_time + np.random.geometric(p)
    :param p:
    :return:
    """
    return np.random.geometric(p)


def choose_random_tower(towers):
    return towers[np.random.choice(len(towers))]


def validate_pos(game, position, sample):
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


def get_random_position_near_path(game, cov_xx, cov_yy, purchased_towers, max_number_of_tries=None):
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


def print_sim_frame(sim_frame):
    info, opponent_hp, dmg_map = sim_frame
    print(info)
    print(opponent_hp)
    print(dmg_map)


def simulate(purchases):
    # One simulation given purchase list
    purchases_ = purchases + [None]

    def get_purchase():
        return purchases_.pop(0)

    dmg_map = np.zeros((map_height, map_width))
    opponent_hp = np.zeros((map_height, map_width))

    gold = 1000
    base_hp = 100

    next_purchase = get_purchase()

    time = 0
    while True:
        # Apply damage to opponent units and obtain gold
        new_opponent_hp = np.maximum(opponent_hp - dmg_map, 0.)
        gold += np.sum(opponent_hp - new_opponent_hp)
        opponent_hp = new_opponent_hp

        # Apply damage to your base and check if you are still alive
        base_hp -= opponent_hp[path[-1]]
        if base_hp <= 0:
            return time

        # Purchase towers if planned
        if not (next_purchase is None):
            while next_purchase and time == next_purchase['time']:
                gold -= tower_types[next_purchase['type']]['cost']
                if gold < 0:
                    print("Rule violation: negative amount of gold")
                    return time
                dmg_map += get_dmg_patch(next_purchase['coords'], next_purchase['type'])
                next_purchase = get_purchase()

        # Move opponent units forward
        for _, (coords_to, coords_from) in enumerate(move_generator):
            opponent_hp[coords_to] = opponent_hp[coords_from]
        opponent_hp[path[0]] = time * 20

        current_state_description = "TIME = {}, HP = {}, GOLD = {}".format(time, base_hp, gold)
        yield current_state_description, opponent_hp, dmg_map

        time += 1
