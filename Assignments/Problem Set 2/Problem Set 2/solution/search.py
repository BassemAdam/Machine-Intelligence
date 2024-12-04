from typing import Tuple, Optional, List,Dict
from game import HeuristicFunction, Game, S, A
from helpers.utils import NotImplemented

#TODO: Import any built in modules you want to use

# All search functions take a problem, a state, a heuristic function and the maximum search depth.
# If the maximum search depth is -1, then there should be no depth cutoff (The expansion should not stop before reaching a terminal state) 

# All the search functions should return the expected tree value and the best action to take based on the search results

# This is a simple search function that looks 1-step ahead and returns the action that lead to highest heuristic value.
# This algorithm is bad if the heuristic function is weak. That is why we use minimax search to look ahead for many steps.
def greedy(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    
    terminal, values = game.is_terminal(state)
    if terminal: return values[agent], None

    actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]
    value, _, action = max((heuristic(game, state, agent), -index, action) for index, (action , state) in enumerate(actions_states))
    return value, action

# Apply Minimax search and return the game tree value and the best action
# Hint: There may be more than one player, and in all the testcases, it is guaranteed that 
# game.get_turn(state) will return 0 (which means it is the turn of the player). All the other players
# (turn > 0) will be enemies. So for any state "s", if the game.get_turn(s) == 0, it should a max node,
# and if it is > 0, it should be a min node. Also remember that game.is_terminal(s), returns the values
# for all the agents. So to get the value for the player (which acts at the max nodes), you need to
# get values[0].
def minimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    
    # I will define a helper function to recursively search the game tree
    def minimax_helper(state: S, depth: int) -> Tuple[float, Optional[A]]:
        
        # Check if current state is terminal state
        is_terminal, values = game.is_terminal(state)
        if is_terminal:
            # if its terminal state then i will return its value and no action is needed
            return values[0], None
        
        # Check depth limit
        # max depth is given so we need to limit search to that max depth
        if max_depth != -1 and depth >= max_depth:
            # if depth is greater than max depth then i will return heuristic value of current state and no action is needed
            return heuristic(game, state, 0), None
        
        # Get available actions
        actions = game.get_actions(state)
        if not actions:
            # as above
            return heuristic(game, state, 0), None
        
        # Get the turn of the player    
        turn = game.get_turn(state)
        # I will initialize the best action to the first action in the list for now until i assign it the best action
        best_action = actions[0]
        
        if turn == 0:  # Max node (player's turn)
            best_value = float('-inf')
            for action in actions:
                # we will loop through all the actions and get the successor state and thier values to maxmize the value of the state
                successor = game.get_successor(state, action)
                # recursively call the helper function to get the value of the successor state
                # to avoid complexity think of it as iam just getting the value of the successor state
                value, _ = minimax_helper(successor, depth + 1)
                # if the value of the successor state is greater than the best value then i will update the best value and best action
                if value > best_value:
                    best_value = value
                    best_action = action
        else:  # Min node (enemy's turn) here is like the above code but we are minimizing the value
            best_value = float('inf')
            for action in actions:
                successor = game.get_successor(state, action)
                value, _ = minimax_helper(successor, depth + 1)
                if value < best_value:
                    best_value = value
                    best_action = action             
        return best_value, best_action
     
    # Start minimax search from root
    value, action = minimax_helper(state, 0)
    return value, action

# Apply Alpha Beta pruning and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    
    # I will define a helper function to recursively search the game tree as above
    # its the same as minimax but with additional logic for alpha and beta pruning
    # so I will skip writing comments for all code that like minimax
    def alpha_beta_helper(state: S, depth: int, alpha: float, beta: float) -> Tuple[float, Optional[A]]:
        
        # Check terminal state as minimax
        is_terminal, values = game.is_terminal(state)
        if is_terminal:
            return values[0], None
        
        # Check depth limit
        if max_depth != -1 and depth >= max_depth:
            return heuristic(game, state, 0), None
        
        # Get available actions
        actions = game.get_actions(state)
        if not actions:
            return heuristic(game, state, 0), None
        
        # Get the turn of the player and initialize the best action to the first action in the list temporarily    
        turn = game.get_turn(state)
        best_action = actions[0]
        
        if turn == 0:  # Max node (player's turn)
            best_value = float('-inf')
            for action in actions:
                successor = game.get_successor(state, action)
                value, _ = alpha_beta_helper(successor, depth + 1, alpha, beta)
                if value > best_value:
                    best_value = value
                    best_action = action
                # update alpha value
                alpha = max(alpha, best_value)
                # if alpha is greater than or equal to beta then we can prune the tree
                # because we know that the value of the current state will not be used
                # so we can break the loop
                # this is the main logic of alpha beta pruning
                if alpha >= beta:  # Pruning
                    break
        else:  # Min node (enemy's turn) is like the above code but we are minimizing the value
            best_value = float('inf')
            for action in actions:
                successor = game.get_successor(state, action)
                value, _ = alpha_beta_helper(successor, depth + 1, alpha, beta)
                if value < best_value:
                    best_value = value
                    best_action = action
                beta = min(beta, best_value)
                if alpha >= beta:  # Pruning
                    break
                    
        return best_value, best_action
    
    # Start alpha-beta search from root with initial bounds
    value, action = alpha_beta_helper(state, 0, float('-inf'), float('inf'))
    return value, action

# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function

    def alpha_beta_helper(state: S, depth: int, alpha: float, beta: float) -> Tuple[float, Optional[A]]:
        # Check terminal state
        is_terminal, values = game.is_terminal(state)
        if is_terminal:
            return values[0], None
        
        # Check depth limit
        if max_depth != -1 and depth >= max_depth:
            return heuristic(game, state, 0), None
        
        # Get available actions
        actions = game.get_actions(state)
        if not actions:
            return heuristic(game, state, 0), None
            
        turn = game.get_turn(state)
        
        # Order moves based on heuristic values
        def get_action_value(action: A) -> float:
            successor = game.get_successor(state, action)
            return heuristic(game, successor, 0)
        
        # sorting imporves the performance of alpha beta pruning coz we are exploring the best moves first for min or max node
        # why ?? moves with higher heuristic values are more likely to be better moves or lead to pruning at min nodes and vice versa    
        # Use stable sort with appropriate ordering based on turn
        if turn == 0:  # Max node
            actions = sorted(actions, key=get_action_value, reverse=True)
        else:  # Min node
            actions = sorted(actions, key=get_action_value)
        
        # the rest is the sames as alpha beta pruning    
        best_action = actions[0]
        
        if turn == 0:  # Max node (player's turn)
            best_value = float('-inf')
            for action in actions:
                successor = game.get_successor(state, action)
                value, _ = alpha_beta_helper(successor, depth + 1, alpha, beta)
                if value > best_value:
                    best_value = value
                    best_action = action
                alpha = max(alpha, best_value)
                if alpha >= beta:  # Pruning
                    break
        else:  # Min node (enemy's turn)
            best_value = float('inf')
            for action in actions:
                successor = game.get_successor(state, action)
                value, _ = alpha_beta_helper(successor, depth + 1, alpha, beta)
                if value < best_value:
                    best_value = value
                    best_action = action
                beta = min(beta, best_value)
                if alpha >= beta:  # Pruning
                    break
                    
        return best_value, best_action
    
    # Start alpha-beta search with move ordering
    value, action = alpha_beta_helper(state, 0, float('-inf'), float('inf'))
    return value, action


# Apply Expectimax search and return the tree value and the best action
# Hint: Read the hint for minimax, but note that the monsters (turn > 0) do not act as min nodes anymore,
# they now act as chance nodes (they act randomly).
def expectimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    # I will skip all the parts that is repeated and go directly to explain chance ndode logic
    def expectimax_helper(state: S, depth: int) -> Tuple[float, Optional[A]]:
        # Check terminal state
        is_terminal, values = game.is_terminal(state)
        if is_terminal:
            return values[0], None
        
        # Check depth limit
        if max_depth != -1 and depth >= max_depth:
            return heuristic(game, state, 0), None
        
        # Get available actions
        actions = game.get_actions(state)
        if not actions:
            return heuristic(game, state, 0), None
            
        turn = game.get_turn(state)
        best_action = actions[0]
        
        if turn == 0:  # Max node (player's turn)
            best_value = float('-inf')
            for action in actions:
                successor = game.get_successor(state, action)
                value, _ = expectimax_helper(successor, depth + 1)
                if value > best_value:
                    best_value = value
                    best_action = action
        else:  # Chance node (enemy's turn)
            # unlike adversial search where we minimize the value of the state here we are averaging the value of the states avaialable for that node
            # Calculate expected value across all actions
            total_value = 0
            num_actions = len(actions)
            for action in actions:
                successor = game.get_successor(state, action)
                value, _ = expectimax_helper(successor, depth + 1)
                total_value += value # sum of all values of the states
            best_value = total_value / num_actions  # Average value for chance node
            
        return best_value, best_action
    
    # Start expectimax search from root
    value, action = expectimax_helper(state, 0)
    return value, action