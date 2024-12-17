from typing import Dict, Optional
from agents import Agent
from environment import Environment
from mdp import MarkovDecisionProcess, S, A
import json
from helpers.utils import NotImplemented
from colorama import init, Fore, Style
init()  # Initialize colorama

# This is a class for a generic Value Iteration agent
class ValueIterationAgent(Agent[S, A]):
    mdp: MarkovDecisionProcess[S, A] # The MDP used by this agent for training 
    utilities: Dict[S, float] # The computed utilities
                                # The key is the string representation of the state and the value is the utility
    discount_factor: float # The discount factor (gamma)

    def __init__(self, mdp: MarkovDecisionProcess[S, A], discount_factor: float = 0.99) -> None:
        super().__init__()
        self.mdp = mdp
        self.utilities = {state:0 for state in self.mdp.get_states()} # We initialize all the utilities to be 0
        self.discount_factor = discount_factor
    
  
    def compute_bellman_with_action(self, state: S) -> tuple[float, A]:
        # For terminal states, return reward
        if self.mdp.is_terminal(state):
            print(f"{Fore.RED}Terminal state reached: {state}{Style.RESET_ALL}")
            return self.mdp.get_reward(state, None, None), None
    
        max_utility = float('-inf')
        best_action = None
        
        # Get valid actions
        actions = self.mdp.get_actions(state)
        print(f"{Fore.GREEN}Available actions for state {state}: {actions}{Style.RESET_ALL}")
        
        if not actions:
            print(f"{Fore.RED}No valid actions for state {state}{Style.RESET_ALL}")
            return 0.0, None
            
        for action in actions:
            action_utility = 0
            # Calculate utility considering transition probabilities
            successors = self.mdp.get_successor(state, action)
            print(f"{Fore.BLUE}Successors for action {action}: {successors}{Style.RESET_ALL}")
            
            for next_state, prob in successors.items():
                reward = self.mdp.get_reward(state, action, next_state)
                action_utility += prob * (reward + self.discount_factor * self.utilities[next_state])
                print(f"{Fore.BLUE}State: {next_state}, Prob: {prob}, Reward: {reward}, Utility: {action_utility}{Style.RESET_ALL}")
            
            if action_utility > max_utility:
                max_utility = action_utility
                best_action = action
                print(f"{Fore.YELLOW}New best action: {action} with utility: {action_utility}{Style.RESET_ALL}")
                    
        return max_utility, best_action

    # Given a state, compute its utility using the bellman equation
    # if the state is terminal, return 0
    def compute_bellman(self, state: S) -> float:
        #TODO: Complete this function
        # instead of repeating the code i have created a function that returns the utility and the best action for the act function also
        # # check if the stat is terminal
        # if self.mdp.is_terminal(state):
        #     return 0
        
        # # compute the utility of the state
        # # the utility of a state is the maximum expected utility of all the actions that can be taken from that state
        # max_utility = float('-inf')
        # for action in self.mdp.get_actions(state):
        #     # so for every action, we need to compute the expected utility of that action
        #     action_utility = 0
        #     for next_state, prob in self.mdp.get_successor(state, action).items():
        #         # the expected utility of an action is the sum of the probability of each next state multiplied by the utility of that state
        #         reward = self.mdp.get_reward(state, action, next_state)
        #         action_utility += prob * (reward + self.discount * self.utilities.get(next_state, 0))
        #     max_utility = max(max_utility, action_utility)
        # return  max_utility
        utility, _ = self.compute_bellman_with_action(state)
        return utility
    # Applies a single utility update
    # then returns True if the utilities has converged (the maximum utility change is less or equal the tolerance)
    # and False otherwise
    def update(self, tolerance: float = 0) -> bool:
        #TODO: Complete this function
        # store the old utilities
        old_utilities = self.utilities.copy()
        max_change = 0
        
        # update the utilities
        for state in self.mdp.get_states():
            self.utilities[state] = self.compute_bellman(state)
            # we calculate the difference between new utility and old ones to know when they converge
            change = abs(self.utilities[state] - old_utilities.get(state, 0))
            max_change = max(max_change, change)
        #if the change is less than tolerance, then the utilities have converged return true
        return max_change <= tolerance

    # This function applies value iteration starting from the current utilities stored in the agent and stores the new utilities in the agent
    # NOTE: this function does incremental update and does not clear the utilities to 0 before running
    # In other words, calling train(M) followed by train(N) is equivalent to just calling train(N+M)
    def train(self, iterations: Optional[int] = None, tolerance: float = 0) -> int:
        #TODO: Complete this function to apply value iteration for the given number of iterations
        iteration = 0
        while iterations is None or iteration < iterations:
            # i will keep updating the utilities until they converge or i finish the number of iterations
            iteration += 1
            if self.update(tolerance):
                break
        return iteration
    
    # Given an environment and a state, return the best action as guided by the learned utilities and the MDP
    # If the state is terminal, return None
    def act(self, env: Environment[S, A], state: S) -> A:
        #TODO: Complete this function
        if self.mdp.is_terminal(state):
          return None
        _, action = self.compute_bellman_with_action(state)
        return action
        
    # Save the utilities to a json file
    def save(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'w') as f:
            utilities = {self.mdp.format_state(state): value for state, value in self.utilities.items()}
            json.dump(utilities, f, indent=2, sort_keys=True)
    
    # loads the utilities from a json file
    def load(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'r') as f:
            utilities = json.load(f)
            self.utilities = {self.mdp.parse_state(state): value for state, value in utilities.items()}
