from dungeon import DungeonProblem, DungeonState
from mathutils import Direction, Point, euclidean_distance, manhattan_distance
from helpers import utils
from collections import deque
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
    
    cache = problem.cache()
    if state in cache:
        return cache[state]
    
    def bfs_distance(start: Point, end: Point) -> float:
        if start == end:
            return 0
        if (start, end) in cache:
            return cache[(start, end)]
        if (end, start) in cache:
            return cache[(end, start)]
        
        queue = deque([(start, 0)])
        visited = {start}
        
        while queue:
            current, dist = queue.popleft()
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_pos = Point(current.x + dx, current.y + dy)
                if (next_pos not in visited and 
                    next_pos in problem.layout.walkable):
                    if next_pos == end:
                        return dist + 1
                    visited.add(next_pos)
                    queue.append((next_pos, dist + 1))
        cache[(start, end)] = float('inf')
        return float('inf')

    def calculate_coins_mst(coins: list[Point]) -> float:
        coins_tuple = tuple(sorted((coin.x, coin.y) for coin in coins))
    
        if coins_tuple in cache:
            return cache[coins_tuple]
        
        if len(coins) <= 1:
            return 0
            
        n = len(coins)
        distances = [[float('inf')] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dist = bfs_distance(coins[i], coins[j])
                distances[i][j] = distances[j][i] = dist
        
        used = [False] * n
        min_edge = [float('inf')] * n
        min_edge[0] = 0
        mst_cost = 0
        
        for _ in range(n):
            v = -1
            for j in range(n):
                if not used[j] and (v == -1 or min_edge[j] < min_edge[v]):
                    v = j
            used[v] = True
            mst_cost += min_edge[v]
            
            for to in range(n):
                if distances[v][to] < min_edge[to]:
                    min_edge[to] = distances[v][to]
        cache[coins_tuple] = mst_cost                
        return mst_cost

    def find_nearest_point(from_point: Point, to_points: list[Point]) -> float:
        if not to_points:
            return 0
        return min(bfs_distance(from_point, p) for p in to_points)

    player_pos = state.player
    exit_pos = state.layout.exit
    coins = list(state.remaining_coins)

    # If no coins remain, return distance to exit
    if not coins:
        return bfs_distance(player_pos, exit_pos)

    # Calculate components:
    # 1. MST cost of remaining coins
    mst_cost = calculate_coins_mst(coins)
    
    # 2. Distance from player to nearest coin
    nearest_coin_dist = find_nearest_point(player_pos, coins)
    
    # 3. Distance from nearest coin to exit
    nearest_exit_dist = find_nearest_point(exit_pos, coins)
    
    # Combine all components
    heuristic = mst_cost + nearest_coin_dist + nearest_exit_dist
    
    cache[state] = heuristic
    return heuristic