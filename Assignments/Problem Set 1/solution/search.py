from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from queue import PriorityQueue
import heapq
from helpers import utils

#TODO: Import any modules you want to use

# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution

def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    #TODO: ADD YOUR CODE HERE
     # Initialize frontier as queue with initial state
    frontier = deque([(initial_state, None, None)])  # (state, parent, action)
    
    # Initialize explored set
    explored = {initial_state}
    
    # Initialize parent dictionary for path reconstruction
    parent = {}  # {state: (parent_state, action)}
    
    while frontier:
        # Get next state from frontier
        current_state, parent_state, action = frontier.popleft()
        
        # Check if current state is goal
        if problem.is_goal(current_state):
            # Reconstruct path
            path = []
            # Traverse back from the goal state to the start state using the parent dictionary
            while parent_state is not None: 
                path.append(action)
                current_state = parent_state # Move to the parent state
                # Get the parent state and the action that led to the current state from the parent dictionary
                parent_state, action = parent.get(current_state, (None, None))
            # Reverse the path to get the correct order from start to goal
            return list(reversed(path))
        
        # Expand current state
        for next_action in problem.get_actions(current_state):
            next_state = problem.get_successor(current_state, next_action) # Get the successor state for the current action
            
            # Add unexplored states to frontier
            if next_state not in explored:
                frontier.append((next_state, current_state, next_action)) # Add the next state, current state, and action to the frontier
                explored.add(next_state) # Mark the next state as explored
                parent[current_state] = (parent_state, action) # Record the parent state and action that led to the next state so that we can use it later above in getting the path
    
    # No solution found
    return None

def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    #TODO: ADD YOUR CODE HERE
    # Initialize frontier as stack with initial state
    frontier = [(initial_state, None, None)]  # (state, parent, action)
    
    # Initialize explored set and parent dictionary
    explored = {initial_state}
    parent = {}  # {state: (parent_state, action)}
    
    while frontier:
        # Get next state from frontier (LIFO)
        current_state, parent_state, action = frontier.pop()
        
        # Check if current state is goal
        if problem.is_goal(current_state):
            # Reconstruct path
            path = []
            # same as in BFS didnt change
            while parent_state is not None:
                path.append(action)
                current_state = parent_state
                parent_state, action = parent.get(current_state, (None, None))
            return list(reversed(path))
        
        # here also same as in BFS 
        # Expand current state
        for next_action in problem.get_actions(current_state):
            next_state = problem.get_successor(current_state, next_action)
           
            # Add unexplored states to frontier
            if next_state not in explored:
                frontier.append((next_state, current_state, next_action))
                explored.add(next_state)
                parent[current_state] = (parent_state, action)
    
    # No solution found
    return None
    
def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    #TODO: ADD YOUR CODE HERE
 
    # Initialize frontier with (cost, sequence, state, parent, action)
    frontier = PriorityQueue()
    sequence = 0
    frontier.put((0, sequence, initial_state, None, None)) # this time we add the cost of the path to the state and also sequence to break tie if we have two states with the same cost
    
    # Track explored states and their cumulative costs
    explored = {initial_state: 0}  # state -> cumulative_cost
    parent = {}   # state -> (parent_state, action)
    
    while not frontier.empty():
        # Get state with lowest cumulative cost
        cost, _, current_state, parent_state, action = frontier.get() # note in priority queue of python it prioritize the first element in the tuple and then second in case of tie
        
        # Skip if we've found a better path to this state
        if current_state in explored and explored[current_state] < cost:
            continue
            
        # Check if goal reached Literally the same as BFS and DFS
        if problem.is_goal(current_state):
            path = []
            while parent_state is not None:
                path.append(action)
                current_state = parent_state
                parent_state, action = parent.get(current_state, (None, None))
            return list(reversed(path))
        
        # Expand current state and loop over all possible actions for that current state 
        for next_action in problem.get_actions(current_state):
            next_state = problem.get_successor(current_state, next_action)
            next_cost = cost + problem.get_cost(current_state, next_action) # get the cumulative cost of the path to the next state
            
            # Add if unexplored or found better cumulative path
            if next_state not in explored or next_cost < explored[next_state]:
                sequence += 1
                frontier.put((next_cost, sequence, next_state, current_state, next_action)) # next_state is the current state and current state is the parent of the next state
                explored[next_state] = next_cost  # Track cumulative cost
                parent[next_state] = (current_state, next_action)  # Fix parent tracking
    
    return None

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #TODO: ADD YOUR CODE HERE

    # Initialize frontier with (f_value, sequence, g_value, state, parent, action)
    frontier = PriorityQueue()
    sequence = 0
    initial_g_value = 0
    initial_f_value = heuristic(problem, initial_state)
    frontier.put((initial_f_value, sequence, initial_g_value, initial_state, None, None))
    
    # Track explored states and their cumulative g-values
    explored = {initial_state: initial_g_value}  # state -> minimum g_value encountered you will find that below in the code we update the g_value if we found a better path to the state
    parent = {}  # state -> (parent_state, action)
    
    while not frontier.empty(): # while the frontier is not empty we will keep searching and expanding the states in the above searches i didnt write this comment 
        # Get state with the lowest f-value
        f_value, _, g_value, current_state, parent_state, action = frontier.get()
        
        # If we already have a lower g-value for this state, skip it to make sure that we are not going to expand the state again if we found a better path to it
        if current_state in explored and explored[current_state] < g_value:
            continue

        # Store parent information for path reconstruction if state is not the initial state aka we store only nodes with parents (inital state has no parent)
        if parent_state is not None:
            parent[current_state] = (parent_state, action)
            # so if iam the current state i will store my parent and the action that led me to this state to know how to return exactly like i came here
            # Point(1, 1): (Point(1, 0), "DOWN"), The current position/state 
            # parent_state: The previous position/state that led here
            # action: The move that got us from parent to current state


        
        # Check if goal is reached
        # notice that iam here only stop when we dequeue the goal state not stop when we enqueue it why ?? because if we checked goal in the enqueue step we will not be sure that this is the best path to the goal maybe there will be better path
        if problem.is_goal(current_state):
            # Reconstruct path from goal to initial state
            path = []
            while parent_state is not None: # we keep going up and saving the actions that led us to the goal state
                path.append(action)
                current_state = parent_state
                parent_state, action = parent.get(current_state, (None, None))
            return list(reversed(path))
        
        # Expand current state after we checked that the current state is not the goal state with all possible actions
        for next_action in problem.get_actions(current_state):
            next_state = problem.get_successor(current_state, next_action)
            next_g = g_value + problem.get_cost(current_state, next_action)  # Cumulative g-cost = g-value is the cumulative cost of last actions + cost of new action
            next_f = next_g + heuristic(problem, next_state) # we prioritize the states with the lowest f-value which is the sum of the g-value and the heuristic value of the state
            
            # Only add next_state to frontier if it has a lower g-value than previously found or it is unexplored
            if next_state not in explored or next_g < explored[next_state]:
                sequence += 1 # increment the sequence to break the tie if we have two states with the same f-value
                frontier.put((next_f, sequence, next_g, next_state, current_state, next_action))
                explored[next_state] = next_g  # Update to the new lowest g-value

    # No solution found
    return None

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #TODO: ADD YOUR CODE HERE
    # or its called Greedy Best First Search its the same as A* but it doesnt consider the cost of the path only the heuristic value its the rabbit 
    # Initialize frontier with (h_value, sequence, state, parent, action)
    frontier = PriorityQueue()
    sequence = 0
    frontier.put((heuristic(problem, initial_state), sequence, initial_state, None, None))
    
    # Track explored states
    explored = {initial_state} # we only need to track the explored states because we dont consider the cost of the path not like above
    parent = {}  # state -> (parent_state, action)
    
    while not frontier.empty():
        # Get state with lowest h-value (and earliest sequence for ties)
        h_value, _, current_state, parent_state, action = frontier.get()
        
        # Check if goal reached
        if problem.is_goal(current_state):
            # Reconstruct path
            path = []
            while parent_state is not None:
                path.append(action)
                current_state = parent_state
                parent_state, action = parent.get(current_state, (None, None))
            return list(reversed(path))
        
        # Expand current state
        for next_action in problem.get_actions(current_state):
            next_state = problem.get_successor(current_state, next_action)
            
            # Add unexplored states to frontier
            if next_state not in explored:
                sequence += 1  # Increment sequence for FIFO ordering
                next_h = heuristic(problem, next_state)
                frontier.put((next_h, sequence, next_state, current_state, next_action))
                explored.add(next_state)
                parent[current_state] = (parent_state, action)
    
    return None