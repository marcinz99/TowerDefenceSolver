import copy
import numpy as np
import tower_defence_solver.utils as utils
from tower_defence_solver.candidate import Candidate


#  UNARY
def addition(game, origin):
    #  print("ADDITION")
    new_purchases = copy.deepcopy(origin.initial_purchases)
    position = utils.get_random_position_near_path(game, game.map_height//2, game.map_width//2, origin.initial_purchases, game.map_height*game.map_width)
    if position is None:
        return None
    tower_id, _ = utils.choose_random_tower(list(game.tower_types.items()))
    to_be_added = {"time": utils.get_random_purchase_time(0.5), "coords": position, "type": tower_id}
    new_purchases.append(to_be_added)
    new_purchases = sorted(new_purchases, key=lambda x: x['time'])

    return Candidate(new_purchases, game)


def deletion(game, origin):
    #  print("DELETION")
    time = origin.time
    purchases_before_simulation_has_finished, purchases_after_simulation_has_finished \
        = split_purchases_into_minimum_n_purchases_before_time(1, time, origin.initial_purchases)

    if purchases_before_simulation_has_finished is None:
        return None

    id_to_be_removed = np.random.choice(len(purchases_before_simulation_has_finished))
    new_purchases = purchases_before_simulation_has_finished.copy()
    new_purchases.pop(id_to_be_removed)
    new_purchases.extend(purchases_after_simulation_has_finished)

    return Candidate(new_purchases, game)


def permutation(game, origin):
    #  print("PERMUTATION")
    time = origin.time
    purchases_before_simulation_has_finished, purchases_after_simulation_has_finished \
        = split_purchases_into_minimum_n_purchases_before_time(2, time, origin.initial_purchases)

    if purchases_before_simulation_has_finished is None:
        return None

    first_id = np.random.choice(len(purchases_before_simulation_has_finished))
    second_id = first_id
    while second_id == first_id:
        second_id = np.random.choice(len(purchases_before_simulation_has_finished))

    new_purchases = copy.deepcopy(purchases_before_simulation_has_finished)
    new_purchases[first_id]["coords"], new_purchases[second_id]["coords"] = new_purchases[second_id]["coords"], new_purchases[first_id]["coords"]
    new_purchases[first_id]["type"], new_purchases[second_id]["type"] = new_purchases[second_id]["type"], new_purchases[first_id]["type"]
    new_purchases.extend(purchases_after_simulation_has_finished)

    return Candidate(new_purchases, game)


def time_translation(game, origin):
    #  print("TRANSLATION")
    time = origin.time

    purchases_before_simulation_has_finished, purchases_after_simulation_has_finished \
        = split_purchases_into_minimum_n_purchases_before_time(1, time, origin.initial_purchases)

    if purchases_before_simulation_has_finished is None:
        return None

    id_to_be_translated = np.random.choice(len(purchases_before_simulation_has_finished))
    new_purchases = copy.deepcopy(purchases_before_simulation_has_finished)

    purchase = copy.deepcopy(new_purchases.pop(id_to_be_translated))
    new_purchase_time = max(purchase.get("time")+np.random.standard_cauchy()*0.5, 1)
    new_purchases.extend(purchases_after_simulation_has_finished)

    purchase['time'] = int(new_purchase_time)
    new_purchases.append(purchase)
    new_purchases = sorted(new_purchases, key=lambda x: x['time'])

    return Candidate(new_purchases, game)


#  BINARY
def cross(game, parent_a, parent_b):
    time = parent_a.time
    A_purchases_before_simulation_has_finished, A_purchases_after_simulation_has_finished \
        = split_purchases_into_minimum_n_purchases_before_time(2, time, parent_a.initial_purchases)

    if A_purchases_before_simulation_has_finished is None:
        return None

    B_purchases_before_simulation_has_finished, B_purchases_after_simulation_has_finished \
        = split_purchases_into_minimum_n_purchases_before_time(2, time, parent_b.initial_purchases)

    if B_purchases_before_simulation_has_finished is None:
        return None

    a_starting_point, a_ending_point = get_split_points(A_purchases_before_simulation_has_finished)
    b_starting_point, b_ending_point = get_split_points(B_purchases_before_simulation_has_finished)

    new_purchases = copy.deepcopy(A_purchases_before_simulation_has_finished)
    for i in range(a_starting_point, a_ending_point):
        new_purchases.pop(a_starting_point)

    for i in range(b_starting_point, b_ending_point):
        new_purchases.append(B_purchases_before_simulation_has_finished[i])

    new_purchases.extend(A_purchases_after_simulation_has_finished)

    return Candidate(new_purchases, game)


def get_split_points(purchases):
    first_id = np.random.choice(len(purchases))
    second_id = first_id

    while second_id == first_id:
        second_id = np.random.choice(len(purchases))

    starting_point = min(first_id, second_id)
    ending_point = max(first_id, second_id)

    return starting_point, ending_point


def split_purchases_into_minimum_n_purchases_before_time(n, time, purchases):
    if len(purchases) < n:
        return None, None

    purchases_before_time = list(filter(lambda purchase: purchase.get("time") < time, purchases))
    purchases_after_time = list(filter(lambda purchase: purchase.get("time") >= time, purchases))

    if len(purchases_before_time) < n:
        purchases_before_time = purchases
        purchases_after_time = []

    return purchases_before_time, purchases_after_time


unary_reproduction = [addition, deletion, permutation, time_translation]
binary_reproduction = [cross]


def reproduction(game, candidates, how_many_to_add):

    how_many_added = 0

    while how_many_added != how_many_to_add:
        x = np.random.binomial(1, 0.0)
        is_binary = x == 1
        is_unary = x == 0

        if is_binary:
            parent_A = np.random.choice(candidates)
            parent_B = parent_A

            while parent_B == parent_A:
                parent_B = np.random.choice(candidates)

            operator = np.random.choice(binary_reproduction)
            element_to_add = operator(game, parent_A, parent_B)

            if element_to_add is not None:
                candidates.append(element_to_add)
                how_many_added += 1

        elif is_unary:
            operator = np.random.choice(unary_reproduction)
            origin = candidates[np.random.choice(len(candidates))]
            #  print(len(origin.initial_purchases))
            element_to_add = operator(game, origin)

            if element_to_add is not None:
                #  print(len(origin.initial_purchases), len(element_to_add.purchases))
                candidates.append(element_to_add)
                how_many_added += 1

    return candidates
