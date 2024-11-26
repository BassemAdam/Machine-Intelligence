from typing import Tuple
import re
from CSP import Assignment, Problem, UnaryConstraint, BinaryConstraint

#TODO (Optional): Import any builtin library or define any helper function you want to use

# This is a class to define for cryptarithmetic puzzles as CSPs
class CryptArithmeticProblem(Problem):
    LHS: Tuple[str, str]
    RHS: str

    # Convert an assignment into a string (so that is can be printed).
    def format_assignment(self, assignment: Assignment) -> str:
        LHS0, LHS1 = self.LHS
        RHS = self.RHS
        letters = set(LHS0 + LHS1 + RHS)
        formula = f"{LHS0} + {LHS1} = {RHS}"
        postfix = []
        valid_values = list(range(10))
        for letter in letters:
            value = assignment.get(letter)
            if value is None: continue
            if value not in valid_values:
                postfix.append(f"{letter}={value}")
            else:
                formula = formula.replace(letter, str(value))
        if postfix:
            formula = formula + " (" + ", ".join(postfix) +  ")" 
        return formula

    @staticmethod
    def from_text(text: str) -> 'CryptArithmeticProblem':
        # Given a text in the format "LHS0 + LHS1 = RHS", the following regex
        # matches and extracts LHS0, LHS1 & RHS
        # For example, it would parse "SEND + MORE = MONEY" and extract the
        # terms such that LHS0 = "SEND", LHS1 = "MORE" and RHS = "MONEY"
        # here code responsible for parsing the text and initializing the problem
        pattern = r"\s*([a-zA-Z]+)\s*\+\s*([a-zA-Z]+)\s*=\s*([a-zA-Z]+)\s*"
        match = re.match(pattern, text)
        if not match: raise Exception("Failed to parse:" + text)
        LHS0, LHS1, RHS = [match.group(i+1).upper() for i in range(3)]

        # Initialize the problem
        problem = CryptArithmeticProblem()
        problem.LHS = (LHS0, LHS1)
        problem.RHS = RHS

        #TODO Edit and complete the rest of this function
        # problem.variables:    should contain a list of variables where each variable is string (the variable name)
        # problem.domains:      should be dictionary that maps each variable (str) to its domain (set of values)
        #                       For the letters, the domain can only contain integers in the range [0,9].
        # problem.constaints:   should contain a list of constraint (either unary or binary constraints).
        
        # Define variables
        # Extract all unique letters from LHS and RHS
       # Define variables
        # Define variables
        # Extract unique letters and set up auxiliary carry variables
        letters = set(LHS0 + LHS1 + RHS)
        max_len = max(len(LHS0), len(LHS1), len(RHS))
        carries = [f'C{i}' for i in range(max_len + 1)]

        # Set variables and domains
        problem.variables = list(letters) + carries
        problem.domains = {letter: set(range(1, 10)) if letter in (LHS0[0], LHS1[0], RHS[0])
                        else set(range(10)) for letter in letters}
        for carry in carries:
            problem.domains[carry] = {0, 1}

        # Initialize constraints
        problem.constraints = []

        # Add all-different constraints for letters
        letter_list = list(letters)
        for i in range(len(letter_list)):
            for j in range(i + 1, len(letter_list)):
                problem.constraints.append(
                    BinaryConstraint((letter_list[i], letter_list[j]), lambda x, y: x != y)
                )

                  # Right-align numbers and process each column
            LHS0_aligned = LHS0.rjust(max_len)
            LHS1_aligned = LHS1.rjust(max_len)
            RHS_aligned = RHS.rjust(max_len)
            
            for i in range(max_len):
                pos = -(i + 1)
                d1 = LHS0_aligned[pos] if LHS0_aligned[pos] != ' ' else None
                d2 = LHS1_aligned[pos] if LHS1_aligned[pos] != ' ' else None
                d3 = RHS_aligned[pos]
                carry_in = carries[i]
                carry_out = carries[i + 1]
            
                # Create partial sum variable for this column
                partial_sum = f'P{i}'  # Partial sum before carry
                problem.variables.append(partial_sum)
                problem.domains[partial_sum] = set(range(19))  # Max sum is 9+9=18
            
                if d1 and d2:
                    # Constraint between first digit and partial sum
                    def make_digit1_constraint(d2_var):
                        def constraint(x, p):
                            return any(x + y == p 
                                    for y in problem.domains[d2_var])
                        return constraint
                    problem.constraints.append(
                        BinaryConstraint((d1, partial_sum), make_digit1_constraint(d2))
                    )
            
                    # Constraint between second digit and partial sum
                    def make_digit2_constraint(d1_var):
                        def constraint(y, p):
                            return any(x + y == p 
                                    for x in problem.domains[d1_var])
                        return constraint
                    problem.constraints.append(
                        BinaryConstraint((d2, partial_sum), make_digit2_constraint(d1))
                    )
            
                # Constraint between partial sum and carry
                def make_carry_constraint():
                    def constraint(p, c):
                        # Check if carry should be 1
                        if i == max_len - 1:  # Last position
                            return c == 1
                        return c == (p // 10)
                    return constraint
                problem.constraints.append(
                    BinaryConstraint((partial_sum, carry_out), make_carry_constraint())
                )
            
                # Constraint between partial sum and result digit
                if d3:
                    def make_result_constraint(carry_var):
                        def constraint(p, r):
                            total = p
                            if carry_var in problem.variables:
                                total += 1  # Add carry-in if it exists
                            return r == (total % 10)
                        return constraint
                    problem.constraints.append(
                        BinaryConstraint((partial_sum, d3), make_result_constraint(carry_in))
                    )
            
                # Constraint between carry-in and result
                if d3:
                    def make_carry_result_constraint(partial_var):
                        def constraint(c, r):
                            if c == 1:
                                for p in problem.domains[partial_var]:
                                    if (p + 1) % 10 == r:
                                        return True
                            else:
                                for p in problem.domains[partial_var]:
                                    if p % 10 == r:
                                        return True
                            return False
                        return constraint
                    problem.constraints.append(
                        BinaryConstraint((carry_in, d3), make_carry_result_constraint(partial_sum))
                    )

        return problem

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())