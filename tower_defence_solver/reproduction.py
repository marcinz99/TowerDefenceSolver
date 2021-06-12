# BO 2021
# Authors: Łukasz Kita, Mateusz Pawłowicz, Michał Szczepaniak, Marcin Zięba
"""
Tower Defence Solver.

Genetic operations.
"""
import copy
import numpy as np
import tower_defence_solver.utils as utils
from tower_defence_solver.candidate import Candidate
from tower_defence_solver import TowerDefenceSolver
from typing import List, Dict, Tuple, Optional, Union

Purchases = List[Dict]
MAX_TRIES = 10


# ========== UNARY OPERATORS ==========


def addition(game: TowerDefenceSolver, origin: Candidate) -> Optional[Candidate]:
    """
    Returns candidate with purchases list the same as origin's purchase list
    concatenated with additional single purchase.

    :param game: Instance of tower defence emulator
    :param origin: candidate, on whose purchases list new candidate purchased will be based on
    :return: candidate with newly added purchase if possible, None otherwise
    """
    time = origin.time
    new_purchases = copy.deepcopy(origin.initial_purchases)
    position = utils.get_random_position_near_path(
        game, game.map_height // 2, game.map_width // 2, origin.initial_purchases, game.map_height * game.map_width
    )
    if position is None:
        return None
    tower_id = np.random.choice(list(game.tower_types.keys()))
    to_be_added = {"time": utils.get_random_purchase_time(time), "coords": position, "type": tower_id}
    new_purchases.append(to_be_added)
    new_purchases = sorted(new_purchases, key=lambda x: x["time"])
    return Candidate(new_purchases, game, time=time)


def deletion(game: TowerDefenceSolver, origin: Candidate) -> Optional[Candidate]:
    """
    Returns candidate with purchases list the same as origin's purchase list, but with one purchase missing
    The purchase to be deleted is taken from these purchases, which had a chance to be done,
    but if there are no such a purchases, it will be randomly taken from the whole purchases list.

    :param game: Instance of tower defence emulator
    :param origin: candidate, on whose purchases list new candidate purchased will be based on
    :return: candidate with delete purchase if possible, None otherwise
    """
    time = origin.time
    (
        purchases_before_simulation_has_finished,
        purchases_after_simulation_has_finished,
    ) = split_purchases_into_minimum_n_elements_at_given_point_in_time(1, time, origin.initial_purchases)

    if purchases_before_simulation_has_finished is None:
        return None

    id_to_be_removed = np.random.choice(len(purchases_before_simulation_has_finished))
    new_purchases = purchases_before_simulation_has_finished.copy()
    new_purchases.pop(id_to_be_removed)
    new_purchases.extend(purchases_after_simulation_has_finished)

    return Candidate(new_purchases, game, time=time)


def permutation(game: TowerDefenceSolver, origin: Candidate) -> Optional[Candidate]:
    """
    Returns candidate with purchases list the same as origin's purchase list, but with time
    of random two purchases being replaced.
    The permutated purchases are taken from these purchases, which had a chance to be done,
    but in case there is not enough of them, they will be randomly taken from the whole purchases list.

    :param game: Instance of tower defence emulator
    :param origin: candidate, on whose purchases list new candidate purchased will be based on
    :return: candidate with permutated two purchases if possible, None otherwise
    """
    time = origin.time
    (
        purchases_before_simulation_has_finished,
        purchases_after_simulation_has_finished,
    ) = split_purchases_into_minimum_n_elements_at_given_point_in_time(2, time, origin.initial_purchases)

    if purchases_before_simulation_has_finished is None:
        return None

    first_id = np.random.choice(len(purchases_before_simulation_has_finished))
    second_id = first_id

    while second_id == first_id:
        second_id = np.random.choice(len(purchases_before_simulation_has_finished))

    new_purchases = copy.deepcopy(purchases_before_simulation_has_finished)

    new_purchases[first_id]["coords"], new_purchases[second_id]["coords"] = (
        new_purchases[second_id]["coords"],
        new_purchases[first_id]["coords"],
    )

    new_purchases[first_id]["type"], new_purchases[second_id]["type"] = (
        new_purchases[second_id]["type"],
        new_purchases[first_id]["type"],
    )

    new_purchases.extend(purchases_after_simulation_has_finished)

    return Candidate(new_purchases, game, time=time)


def time_translation(game: TowerDefenceSolver, origin: Candidate) -> Optional[Candidate]:
    """
    Returns candidate with purchases list the same as origin's purchase list, but with time of one random
    purchase being changed.
    The chosen purchase can be as well postponed as preponed.

    :param game: Instance of tower defence emulator
    :param origin: candidate, on whose purchases list new candidate purchased will be based on
    :return: candidate with one purchase translated in time if possible, None otherwise
    """
    time = origin.time

    (
        purchases_before_simulation_has_finished,
        purchases_after_simulation_has_finished,
    ) = split_purchases_into_minimum_n_elements_at_given_point_in_time(1, time, origin.initial_purchases)

    if purchases_before_simulation_has_finished is None:
        return None

    id_to_be_translated = np.random.choice(len(purchases_before_simulation_has_finished))
    new_purchases = copy.deepcopy(purchases_before_simulation_has_finished)

    purchase = copy.deepcopy(new_purchases.pop(id_to_be_translated))
    new_purchase_time = max(purchase.get("time") + np.random.standard_cauchy() * 0.5, 1)
    new_purchases.extend(purchases_after_simulation_has_finished)

    purchase["time"] = int(new_purchase_time)
    new_purchases.append(purchase)
    new_purchases = sorted(new_purchases, key=lambda x: x["time"])

    return Candidate(new_purchases, game, time=time)


def replace_tower_with_another(game: TowerDefenceSolver, origin: Candidate) -> Optional[Candidate]:
    """
    Returns candidate with purchases list the same as origin's purchase list, but with one extra purchase made
    in place of other already existing (selling mechanic).
    The created purchase can be as well postponed as preponed.

    :param game: Instance of tower defence emulator
    :param origin: candidate, on whose purchases list new candidate purchased will be based on
    :return: candidate with one purchase translated in time if possible, None otherwise
    """
    time = origin.time
    (
        purchases_before_simulation_has_finished,
        purchases_after_simulation_has_finished,
    ) = split_purchases_into_minimum_n_elements_at_given_point_in_time(1, time, origin.initial_purchases)

    if purchases_before_simulation_has_finished is None:
        return None

    id_to_be_translated = np.random.choice(len(purchases_before_simulation_has_finished))
    new_purchases = copy.deepcopy(purchases_before_simulation_has_finished)

    purchase = copy.deepcopy(new_purchases[id_to_be_translated])
    current_type = purchase["type"]

    new_purchase_time = purchase.get("time") + 5 + utils.get_random_initial_purchase_time(0.2)
    new_purchases.extend(purchases_after_simulation_has_finished)

    purchase["time"] = int(new_purchase_time)
    purchase["type"] = np.random.choice([tower[0] for tower in game.tower_types.items()
                                         if tower[1]["cost"] >= game.tower_types[current_type]["cost"]])
    new_purchases.append(purchase)
    new_purchases = sorted(new_purchases, key=lambda x: x["time"])

    return Candidate(new_purchases, game, time=time)


# ========== BINARY OPERATORS ==========


def cross(game: TowerDefenceSolver, parent_a: Candidate, parent_b: Candidate) -> Optional[Candidate]:
    """
    Returns candidate with purchases list being the combination of parents' purchases list.
    The purchases list of the newly created candidate is the purchases list of the first parent, with
    some sequence of orders being replaced with the sequence derived from the second parent.
    The sequences are tried to be taken from these purchases which had a chance to be done, but if there are
    not enough of them they will be taken from the whole purchases list.

    :param game: Instance of tower defence emulator
    :param parent_a: first parent
    :param parent_b: second parent
    :return: candidate with purchases being the combination of parents' purchases if possible, None otherwise
    """
    time = parent_a.time
    (
        parent_a_purchases_before_simulation_has_finished,
        parent_a_purchases_after_simulation_has_finished,
    ) = split_purchases_into_minimum_n_elements_at_given_point_in_time(2, time, parent_a.initial_purchases)

    if parent_a_purchases_before_simulation_has_finished is None:
        return None

    (
        parent_b_purchases_before_simulation_has_finished,
        _,
    ) = split_purchases_into_minimum_n_elements_at_given_point_in_time(2, time, parent_b.initial_purchases)

    if parent_b_purchases_before_simulation_has_finished is None:
        return None

    a_starting_point, a_ending_point = get_split_points(parent_a_purchases_before_simulation_has_finished)
    new_purchases = copy.deepcopy(parent_a_purchases_before_simulation_has_finished)

    for i in range(a_starting_point, a_ending_point):
        new_purchases.pop(a_starting_point)

    new_purchases.extend(parent_a_purchases_after_simulation_has_finished)
    new_purchases_copy = copy.deepcopy(new_purchases)
    was_everything_added = False
    how_many_tries = 0

    while not was_everything_added and how_many_tries < MAX_TRIES:
        new_purchases = copy.deepcopy(new_purchases_copy)
        b_starting_point, b_ending_point = get_split_points(parent_b_purchases_before_simulation_has_finished)
        was_everything_added = True

        for i in range(b_starting_point, b_ending_point):
            purchase_to_be_added = parent_b_purchases_before_simulation_has_finished[i]
            purchase_coords = purchase_to_be_added["coords"]

            if not utils.validate_pos(game, purchase_coords, new_purchases):
                was_everything_added = False
                break

            new_purchases.append(purchase_to_be_added)
        how_many_tries += 1

    if how_many_tries >= MAX_TRIES:
        return None

    return Candidate(new_purchases, game, time=time)


def get_split_points(purchases: Purchases) -> Tuple[int, int]:
    """
    Finds indexes allowing the split of the purchases list into three parts

    :param purchases: list of purchases
    :return: two different indexes indicating points in time which could be
             used to cut a part of the given purchases list
    """
    first_id = np.random.choice(len(purchases))
    second_id = first_id

    while second_id == first_id:
        second_id = np.random.choice(len(purchases))

    starting_point = min(first_id, second_id)
    ending_point = max(first_id, second_id)

    return starting_point, ending_point


def split_purchases_into_minimum_n_elements_at_given_point_in_time(
        n: int, time: int, purchases: Purchases
) -> Union[Tuple[Purchases, Purchases], Tuple[None, None]]:
    """
    Splits the given purchases list into two parts in the given point of time,
    with the first part consisting of at least n elements.

    :param n: number of elements which must be in the first part of the split list
    :param time: point in time
    :param purchases: list of purchases
    :return: tuple consisting of two parts of the split list if possible, None otherwise
    """
    if len(purchases) < n:
        return None, None

    purchases_before_time = list(filter(lambda purchase: purchase.get("time") < time, purchases))
    purchases_after_time = list(filter(lambda purchase: purchase.get("time") >= time, purchases))

    if len(purchases_before_time) < n:
        purchases_before_time = purchases
        purchases_after_time = []

    return purchases_before_time, purchases_after_time


UNARY_REPRODUCTION = [addition, deletion, permutation, time_translation, replace_tower_with_another]
BINARY_REPRODUCTION = [cross]


def reproduction(game: TowerDefenceSolver, candidates: List[Candidate], how_many_to_add: int,
                 weighted_by: str = None) -> List[Candidate]:
    """
    Reproduce the provided candidates by the given amount.


    :param game:
    :param candidates:
    :param how_many_to_add:
    :param weighted_by: 'order' - weighted by order in list of candidates sorted by survival time,
                        'time' - weighted by survival time, None - uniform
    :return:
    """
    how_many_added = 0

    while how_many_added != how_many_to_add:
        candidates = sorted(candidates, key=lambda candidate: candidate.time)
        if weighted_by == 'order':
            order_range = np.arange(len(candidates), 0, -1)
            probability_distribution = order_range / np.sum(order_range)
        elif weighted_by == 'time':
            times_array = np.array(list(map(lambda candidate: candidate.time, candidates)))
            probability_distribution = times_array / np.sum(times_array)
        else:
            probability_distribution = None

        x = np.random.choice([0, 1], p=game.p_binary)
        is_binary = x == 0
        is_unary = x == 1
        if is_binary:
            parent_a = np.random.choice(candidates, p=probability_distribution)
            parent_b = parent_a

            while parent_b == parent_a:
                parent_b = np.random.choice(candidates, p=probability_distribution)

            operator = np.random.choice(BINARY_REPRODUCTION, p=game.p_binary_ops)

            element_to_add = operator(game, parent_a, parent_b)

            if element_to_add is not None:
                candidates.append(element_to_add)
                how_many_added += 1

        elif is_unary:
            operator = np.random.choice(UNARY_REPRODUCTION, p=game.p_unary_ops)
            origin = np.random.choice(candidates, p=probability_distribution)
            element_to_add = operator(game, origin)
            if element_to_add is not None:
                candidates.append(element_to_add)
                how_many_added += 1

    return candidates
