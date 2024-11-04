from dungeon import DungeonProblem, DungeonState
from mathutils import Direction, Point, euclidean_distance, manhattan_distance
from helpers import utils

# This heuristic returns the distance between the player and the exit as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: DungeonProblem, state: DungeonState):
    return euclidean_distance(state.player, problem.layout.exit)

#TODO: Import any modules and write any functions you want to use

def strong_heuristic(problem: DungeonProblem, state: DungeonState) -> float:
    #TODO: ADD YOUR CODE HERE
    #IMPORTANT: DO NOT USE "problem.is_goal" HERE.
    # Calling it here will mess up the tracking of the explored nodes count
    # which is considered the number of is_goal calls during the search
    #NOTE: you can use problem.cache() to get a dictionary in which you can store information that will persist between calls of this function
    # This could be useful if you want to store the results heavy computations that can be cached and used across multiple calls of this function
    
    # Get coordinates of the player and the exit
    player_pos = state.player
    exit_pos = problem.layout.exit
    remaining_coins = state.remaining_coins

    # Check if there are no remaining coins; if so, estimate direct cost to exit
    if not remaining_coins:
        return manhattan_distance(player_pos, exit_pos)

    # Calculate distance to the closest coin
    min_dist_to_coin = min(manhattan_distance(player_pos, coin) for coin in remaining_coins)

    # Calculate the minimum spanning distance between all coins and the exit
    coin_to_coin_distances = []
    coins = list(remaining_coins)

    # Approximate the minimum spanning path by summing nearest neighbors (greedy approximation)
    remaining_coins_set = set(remaining_coins)
    current_pos = player_pos
    total_coin_distance = 0

    # Greedily find the nearest coin path
    while remaining_coins_set:
        nearest_coin = min(remaining_coins_set, key=lambda coin: manhattan_distance(current_pos, coin))
        total_coin_distance += manhattan_distance(current_pos, nearest_coin)
        current_pos = nearest_coin
        remaining_coins_set.remove(nearest_coin)

    # Estimate the cost from the last coin to the exit
    last_to_exit_distance = manhattan_distance(current_pos, exit_pos)

    # Heuristic is the distance to closest coin + estimated cost to collect all coins + exit cost
    heuristic_value = min_dist_to_coin + total_coin_distance + last_to_exit_distance

    # Cache the heuristic value
    cache = problem.cache()
    if state not in cache:
        cache[state] = heuristic_value

    return cache[state]