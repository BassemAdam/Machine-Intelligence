from typing import Any, Dict, Set, Tuple, List
from problem import Problem
from mathutils import Direction, Point
from helpers import utils

#TODO: (Optional) Instead of Any, you can define a type for the parking state
ParkingState = Tuple[Point]
# An action of the parking problem is a tuple containing an index 'i' and a direction 'd' where car 'i' should move in the direction 'd'.
ParkingAction = Tuple[int, Direction]

# This is the implementation of the parking problem
class ParkingProblem(Problem[ParkingState, ParkingAction]):
    passages: Set[Point]    # A set of points which indicate where a car can be (in other words, every position except walls).
    cars: Tuple[Point]      # A tuple of points where state[i] is the position of car 'i'. 
    slots: Dict[Point, int] # A dictionary which indicate the index of the parking slot (if it is 'i' then it is the slot of car 'i') for every position.
                            # if a position does not contain a parking slot, it will not be in this dictionary.
    width: int              # The width of the parking lot.
    height: int             # The height of the parking lot.

    # This function should return the initial state
    def get_initial_state(self) -> ParkingState:
        #TODO: ADD YOUR CODE HERE
        return tuple(self.cars)
    
    # This function should return True if the given state is a goal. Otherwise, it should return False.
    def is_goal(self, state: ParkingState) -> bool:
        # Loop through all the cars' positions
        for i, car in enumerate(state):
            print(f"\033[91mChecking car {i} at position {car}\033[0m")  
            print(self.slots)
            index_of_parked_car = self.slots.get(car, None)  # Get the index of the car parked at the current position
            #print(f"\033[91mExpected slot position for car {i}: {slot_position}\033[0m")  
            if i != index_of_parked_car:  # Check if the car is in its slot and not in the slot of another car
                print(f"\033[91mCar {i} is not in its slot. Goal state: False\033[0m")  
                return False
        print(f"\033[91mAll cars are in their slots. Goal state: True\033[0m")  
        return True
        
    
    # This function returns a list of all the possible actions that can be applied to the given state
    def get_actions(self, state: ParkingState) -> List[ParkingAction]:
        #TODO: ADD YOUR CODE HERE
        actions = []
        for i, car in enumerate(state): # loop through all the cars
            for direction in Direction: # loop through all the allowed directions
                new_position = car + direction.to_vector() # calculate the new position of the car after the action
                if new_position in self.passages and new_position not in state : # check if the new position is a passage and no car is already there
                    actions.append((i, direction))
        return actions
    
    # This function returns a new state which is the result of applying the given action to the given state
    def get_successor(self, state: ParkingState, action: ParkingAction) -> ParkingState:
        #TODO: ADD YOUR CODE HERE
        car_index, direction = action
        car_position = state[car_index]
        new_position = car_position + direction.to_vector()
        new_state = list(state)
        new_state[car_index] = new_position
        return tuple(new_state)
    
    # This function returns the cost of applying the given action to the given state
    def get_cost(self, state: ParkingState, action: ParkingAction) -> float:
        #TODO: ADD YOUR CODE HERE
        car_index, direction = action
        car_position = state[car_index]
        
        # debugging
        # print(f"\033[91m{direction.to_vector()}\033[0m")
        # print(f"\033[91m{car_position}\033[0m")
        
        new_position = car_position + direction.to_vector()
        
        # Check if the new position is another car's parking slot
        if new_position in self.slots and self.slots[new_position] != car_index:
            return 101.0
        return 1.0
    
     # Read a parking problem from text containing a grid of tiles
    @staticmethod
    def from_text(text: str) -> 'ParkingProblem':
        passages =  set()
        cars, slots = {}, {}
        lines = [line for line in (line.strip() for line in text.splitlines()) if line]
        width, height = max(len(line) for line in lines), len(lines)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char != "#":
                    passages.add(Point(x, y))
                    if char == '.':
                        pass
                    elif char in "ABCDEFGHIJ":
                        cars[ord(char) - ord('A')] = Point(x, y)
                    elif char in "0123456789":
                        slots[int(char)] = Point(x, y)
        problem = ParkingProblem()
        problem.passages = passages
        problem.cars = tuple(cars[i] for i in range(len(cars)))
        problem.slots = {position:index for index, position in slots.items()}
        problem.width = width
        problem.height = height
        return problem

    # Read a parking problem from file containing a grid of tiles
    @staticmethod
    def from_file(path: str) -> 'ParkingProblem':
        with open(path, 'r') as f:
            return ParkingProblem.from_text(f.read())
    
