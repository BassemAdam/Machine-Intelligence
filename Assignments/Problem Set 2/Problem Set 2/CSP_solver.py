from typing import Any, Dict, List, Optional, Tuple
from CSP import Assignment, BinaryConstraint, Problem, UnaryConstraint
from helpers.utils import NotImplemented

# This function applies 1-Consistency to the problem.
# In other words, it modifies the domains to only include values that satisfy their variables' unary constraints.
# Then all unary constraints are removed from the problem (they are no longer needed).
# The function returns False if any domain becomes empty. Otherwise, it returns True.
def one_consistency(problem: Problem) -> bool:
    remaining_constraints = []
    solvable = True
    for constraint in problem.constraints:
        if not isinstance(constraint, UnaryConstraint):
            remaining_constraints.append(constraint)
            continue
        variable = constraint.variable
        print(f"\033[91m{variable}\033[0m")
        new_domain = {value for value in problem.domains[variable] if constraint.condition(value)}
        if not new_domain:
            solvable = False
        problem.domains[variable] = new_domain
    problem.constraints = remaining_constraints
    return solvable

# This function returns the variable that should be picked based on the MRV heuristic.
# NOTE: We don't use the domains inside the problem, we use the ones given by the "domains" argument 
#       since they contain the current domains of unassigned variables only.
# NOTE: If multiple variables have the same priority given the MRV heuristic, 
#       we order them in the same order in which they appear in "problem.variables".
def minimum_remaining_values(problem: Problem, domains: Dict[str, set]) -> str:
    _, _, variable = min((len(domains[variable]), index, variable) for index, variable in enumerate(problem.variables) if variable in domains)
    return variable

# This function should implement forward checking
# The function is given the problem, the variable that has been assigned and its assigned value and the domains of the unassigned values
# The function should return False if it is impossible to solve the problem after the given assignment, and True otherwise.
# In general, the function should do the following:
#   - For each binary constraints that involve the assigned variable:
#       - Get the other involved variable.
#       - If the other variable has no domain (in other words, it is already assigned), skip this constraint.
#       - Update the other variable's domain to only include the values that satisfy the binary constraint with the assigned variable.
#   - If any variable's domain becomes empty, return False. Otherwise, return True.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def forward_checking(problem: Problem, assigned_variable: str, assigned_value: Any, domains: Dict[str, set]) -> bool:
    #TODO: Write this function
     # Check unary constraints first
    for constraint in problem.constraints:
        if isinstance(constraint, UnaryConstraint):
            # Only check constraints for unassigned variables
            if constraint.variable in domains:
                # Create new domain keeping only consistent values
                new_domain = {value for value in domains[constraint.variable] 
                            if constraint.is_satisfied({constraint.variable: value})}
                domains[constraint.variable] = new_domain
                if not domains[constraint.variable]:
                    return False

    # Check binary constraints
    for constraint in problem.constraints:
        if isinstance(constraint, BinaryConstraint): # x/y = 0 
            if assigned_variable not in constraint.variables: # x
                continue
            
            # Get the other variable
            other_var = constraint.get_other(assigned_variable) # y
            
            # Skip if other variable already assigned
            if other_var not in domains:
                continue
           
            # Create new domain keeping only consistent values
            new_domain = {value for value in domains[other_var] 
                         if constraint.is_satisfied({assigned_variable: assigned_value, 
                                                   other_var: value})} # x , y = 0
            domains[other_var] = new_domain
            
            if not domains[other_var]:
                return False
    
    return True

# This function should return the domain of the given variable order based on the "least restraining value" heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# Generally, this function is very similar to the forward checking function, but it differs as follows:
#   - You are not given a value for the given variable, since you should do the process for every value in the variable's
#     domain to see how much it will restrain the neigbors domain
#   - Here, you do not modify the given domains. But you can create and modify a copy.
# IMPORTANT: If multiple values have the same priority given the "least restraining value" heuristic, 
#            order them in ascending order (from the lowest to the highest value).
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def least_restraining_values(problem: Problem, variable_to_assign: str, domains: Dict[str, set]) -> List[Any]:
    #TODO: Write this function
    # Store (value, remaining_values_count) pairs
    value_scores: List[Tuple[Any, int]] = []
    
    # For each possible value in variable's domain
    for value in domains[variable_to_assign]:
        total_remaining = 0
        domains_copy = {var: set(domain) for var, domain in domains.items()}
        
        # Check how this value affects other variables' domains
        for constraint in problem.constraints:
            if isinstance(constraint, BinaryConstraint):
                if variable_to_assign not in constraint.variables:
                    continue
                
                # Get the other variable
                other_var = constraint.get_other(variable_to_assign)
                
                # Skip if other variable already assigned
                if other_var not in domains_copy:
                    continue
                
                # Count values that remain valid in other variable's domain
                valid_values = {other_val for other_val in domains_copy[other_var]
                              if constraint.is_satisfied({variable_to_assign: value,
                                                       other_var: other_val})}
                
                # Update domain and count remaining values
                domains_copy[other_var] = valid_values
                total_remaining += len(valid_values)
        
        value_scores.append((value, total_remaining))
    
    # Sort by:
    # 1. Descending order of remaining values (least restraining first)
    # 2. Ascending order of value (for tie breaking)
    value_scores.sort(key=lambda x: (-x[1], x[0]))
    
    # Return just the values in sorted order
    return [value for value, _ in value_scores]

# This function should solve CSP problems using backtracking search with forward checking.
# The variable ordering should be decided by the MRV heuristic.
# The value ordering should be decided by the "least restraining value" heurisitc.
# Unary constraints should be handled using 1-Consistency before starting the backtracking search.
# This function should return the first solution it finds (a complete assignment that satisfies the problem constraints).
# If no solution was found, it should return None.
# IMPORTANT: To get the correct result for the explored nodes, you should check if the assignment is complete only once using "problem.is_complete"
#            for every assignment including the initial empty assignment, EXCEPT for the assignments pruned by the forward checking.
#            Also, if 1-Consistency deems the whole problem unsolvable, you shouldn't call "problem.is_complete" at all.
def solve(problem: Problem) -> Optional[Assignment]:
    #TODO: Write this function
    # Initial empty assignment
    assignment: Dict[str, Any] = {}

    # Apply 1-Consistency (handle unary constraints)
    Result = one_consistency(problem)

    # Initialize domains for unassigned variables
    domains: Dict[str, set] = {var: set(problem.domains[var]) for var in problem.variables}
    # for constraint in problem.constraints:
    #     if isinstance(constraint, UnaryConstraint):
    #         var = constraint.variable
    #         domains[var] = {value for value in domains[var] 
    #                       if constraint.is_satisfied({var: value})}
    #         if not domains[var]:
    #             return None  # No solution possible
    
    def backtrack(curr_assignment: Dict[str, Any], curr_domains: Dict[str, set]) -> Optional[Assignment]:
        # Check if assignment is complete
        if problem.is_complete(curr_assignment):
            return curr_assignment
        
        # Select unassigned variable using MRV
        unassigned = [var for var in problem.variables if var not in curr_assignment]
        if not unassigned:
            return None
        
        # Apply MRV heuristic # Initialize domains for unassigned variables
        #var = min(unassigned, key=lambda v: len(curr_domains[v]))
        var = minimum_remaining_values(problem, curr_domains)

        # Initialize domains for unassigned variables
        # Get ordered values using least restraining values heuristic
        values = least_restraining_values(problem, var, curr_domains)
        
        # Try each value
        for value in values:
            # Create new assignment with this value
            new_assignment = curr_assignment.copy()
            new_assignment[var] = value
            
            # Create new domains for forward checking
            new_domains = {v: set(d) for v, d in curr_domains.items() if v != var}
            
            # Apply forward checking
            if forward_checking(problem, var, value, new_domains):
                result = backtrack(new_assignment, new_domains)
                if result is not None:
                    return result
                    
        return None
    
    # # Check initial empty assignment
    # if problem.is_complete(assignment):
    #     return assignment
    if Result == False:
        return None   
    # Start backtracking search
    return backtrack(assignment, domains)