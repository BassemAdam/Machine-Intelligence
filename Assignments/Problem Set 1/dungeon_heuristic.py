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
    if state in cache: # If the state is already in the cache, return the value thats level 1 caching i did you will find below that i will start caching points also to speed up searching for the nearest point
        return cache[state]
    
    def bfs_distance(start: Point, end: Point) -> float:
        # If the start and end points are the same, return 0
        if start == end:
            return 0
        if (start, end) in cache:
            return cache[(start, end)] # If the distance between the two points is already calculated, return it
        if (end, start) in cache:
            return cache[(end, start)] # distance is the same in both directions , some cases in that dungeion it will be like that s->e or e->s
        
        # Perform BFS to find the shortest path between the two points
        queue = deque([(start, 0)]) # A queue with a tuple of the current point and the distance from the start point
        visited = {start} # to keep track of the visited points amd avoid revisiting them
        
        while queue:
            current, dist = queue.popleft()
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]: # Check all 4 directions
                next_pos = Point(current.x + dx, current.y + dy)
                if (next_pos not in visited and 
                    next_pos in problem.layout.walkable): # If the next position is not visited and is walkable
                    if next_pos == end: # If the next position is the end point, return the distance + 1 and we finished
                        return dist + 1
                    visited.add(next_pos)
                    queue.append((next_pos, dist + 1)) #else Add the next position to the queue with the distance + 1 and repeat again
        cache[(start, end)] = float('inf') # If no path is found, return infinity
        return float('inf')

    # Calculate the MST cost of the remaining coins
    # tbh i didnt remember how to implement algorithm MST that is connecting coins with minimum distance so i used internet 
    # i think there are more effecient ones like floyd warshall or prim's algorithm but i will stick with this one because its the simplest for me
    # i will explain it to you based on what i have understood from the code
    def calculate_coins_mst(coins: list[Point]) -> float:
        # creates a tuple of the coordinates of the coins, sorted to ensure a consistent order.
        # we sort the coins so that when we check if the coins are already in the cache we dont have to check for all the permutations of the coins
        coins_tuple = tuple(sorted((coin.x, coin.y) for coin in coins))

        # If the MST cost of the coins is already calculated, return it (thats why we sorted it)
        if coins_tuple in cache:
            return cache[coins_tuple]
        
        # If there is only one coin, logically there will be no connections between the coins
        if len(coins) <= 1:
            return 0
            
        n = len(coins)
        # Create a 2D array to store the distances between the coins
        # [float('inf')] * n creates a list of n elements, each initialized to infinity -> one row in the matrix
        # outer loop creates n such rows -> the entire matrix
        distances = [[float('inf')] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                # get the distance between each coin and all other coins
                dist = bfs_distance(coins[i], coins[j])
                # ofcourse distance is symmetric so we store it in both directions
                distances[i][j] = distances[j][i] = dist

        #now we have the distance between each coin and all other coins
        # so we can start calculating the minimum spanning tree

        # Prim's algorithm to find the minimum spanning tree
        # n is the number of coins
        used = [False] * n # to keep track of the visited coins list of size n
        min_edge = [float('inf')] * n # to keep track of the minimum edge cost of each coin

        # The first coin is chosen as the starting point, so its minimum edge cost is set to zero.
        min_edge[0] = 0
        mst_cost = 0


        for _ in range(n): # loop for n coins and when we dont use the iterator number lets name it just _ not imp
            
            # select coin "v" 
            v = -1 # it will be the first coin with mst cost 0 which is better than infinity
            for j in range(n):
                # that is not visited and has the minimum edge cost
                if not used[j] and (v == -1 or min_edge[j] < min_edge[v]):
                    v = j

            # here we have coin with the smallest minimum edge cost
            used[v] = True # mark it as visited
            mst_cost += min_edge[v] # add the minimum edge cost to the total cost
            
            # its much easier to understand if you wrote the matrices and started calculating it by hand
            # in algorithms course we did that
            # we try to see if there is from s to d a path that is shorter than the current path
            for to in range(n):
                # If distances[v][to] is smaller, it means that connecting to to the MST through v is cheaper than the previously known minimum cost
                if distances[v][to] < min_edge[to]:
                    min_edge[to] = distances[v][to]

        # Cache the MST cost of the coins
        cache[coins_tuple] = mst_cost                
        return mst_cost

    def find_nearest_point(from_point: Point, to_points: list[Point]) -> float:
        if not to_points:
            return 0
        # this is a simple nearest point distance where we find the nearest point to the from_point
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
    
    # Combine all components i thought that Mst cost of the reminaing coins may determine how close iam to finish the game
    # also the distance from play to nearest coin and the distance from the nearest coin to the exit
    # there might be much effecient ways but idk i stucked alot so i mixed stuff together and it worked suddenly lol
    heuristic = mst_cost + nearest_coin_dist + nearest_exit_dist
    
    cache[state] = heuristic
    return heuristic