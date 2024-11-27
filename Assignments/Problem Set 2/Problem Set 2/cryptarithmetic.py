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

        # Setup variables and domains
        problem._initialize_variables(LHS0, LHS1, RHS)
        problem._initialize_domains()
        
        # Add constraints
        problem._add_all_different_constraints()
        problem._add_column_constraints()
        
        return problem

    def _initialize_variables(self, LHS0: str, LHS1: str, RHS: str) -> None:
        # Get unique letters and calculate lengths
        self.letters = set(LHS0 + LHS1 + RHS)
        self.max_len = max(len(LHS0), len(LHS1), len(RHS))
        
        # Pad terms for alignment
        self.LHS0_padded = LHS0.rjust(self.max_len, '0')
        self.LHS1_padded = LHS1.rjust(self.max_len, '0')
        self.RHS_padded = RHS.rjust(self.max_len, '0')
        
        # Create auxiliary variables
        self.carries = [f'C{i}' for i in range(self.max_len + 1)]
        self.sums = [f'SUM{i}' for i in range(self.max_len)]
        
        # Set all variables
        self.variables = list(self.letters) + self.carries + self.sums

    def _initialize_domains(self) -> None:
        self.domains = {}
        
        # Get actual first letters (not padded)
        LHS0_first = self.LHS[0][0]  # First letter of first term (e.g., P from POINT)
        LHS1_first = self.LHS[1][0]  # First letter of second term (e.g., Z from ZERO)
        RHS_first = self.RHS[0]      # First letter of result (e.g., E from ENERGY)
        
        # Leading letters cannot be zero
        leading_letters = {LHS0_first, LHS1_first, RHS_first}
        
        # Set domains for letters
        for letter in self.letters:
            # Leading letters get domain [1-9], others [0-9]
            self.domains[letter] = set(range(1, 10)) if letter in leading_letters else set(range(10))
        
        # Carry domains
        for carry in self.carries:
            self.domains[carry] = {0, 1}
        
        # Sum domains
        for sum_var in self.sums:
            self.domains[sum_var] = set(range(10))
  
    def _add_all_different_constraints(self) -> None:
        self.constraints = []
        letter_list = list(self.letters)
        
        for i in range(len(letter_list)):
            for j in range(i + 1, len(letter_list)):
                self.constraints.append(
                    BinaryConstraint(
                        (letter_list[i], letter_list[j]),
                        lambda x, y: x != y
                    )
                )

    def _add_column_constraints(self) -> None:
        for i in range(self.max_len):
            pos = self.max_len - i - 1
            digits = self._get_column_digits(pos)
            self._add_single_column_constraints(i, digits)

    def _get_column_digits(self, pos: int) -> tuple:
        d1 = self.LHS0_padded[pos] if self.LHS0_padded[pos] != '0' else None
        d2 = self.LHS1_padded[pos] if self.LHS1_padded[pos] != '0' else None
        d3 = self.RHS_padded[pos]
        return d1, d2, d3

    def _add_single_column_constraints(self, col_idx: int, digits: tuple) -> None:
        d1, d2, d3 = digits
        carry_in = self.carries[col_idx]
        carry_out = self.carries[col_idx + 1]
        sum_var = self.sums[col_idx]
        
        if d1 and d2:
            self._add_two_digit_column_constraints(d1, d2, d3, carry_in, carry_out, sum_var, col_idx)
        elif d1:
            self._add_single_digit_column_constraints(d1, d3, carry_in, carry_out, sum_var, col_idx)
        elif d2:
            self._add_single_digit_column_constraints(d2, d3, carry_in, carry_out, sum_var, col_idx)
        else:
            self._add_carry_only_constraints(carry_in, carry_out)

    def _add_two_digit_column_constraints(self, d1, d2, d3, carry_in, carry_out, sum_var, col_idx):
        # Create temporary sum variable to break down the constraint
        temp_sum = f'TEMP{col_idx}'
        self.variables.append(temp_sum)
        self.domains[temp_sum] = set(range(19))  # Max possible sum is 18 (9+9)
        
        self.constraints.extend([
            # d1 + d2 = temp_sum
            BinaryConstraint(
                (d1, d2),
                lambda x, y: x + y in self.domains[temp_sum]
            ),
            
            # temp_sum + carry_in = result + 10*carry_out
            BinaryConstraint(
                (temp_sum, carry_in),
                lambda t, c: any(
                    t + c == s + 10 * co 
                    for s in self.domains[sum_var]
                    for co in self.domains[carry_out]
                )
            ),
            
            # sum_var should equal d3
            BinaryConstraint(
                (sum_var, d3),
                lambda s, r: s == r
            ),
            
            # Set carry_out based on temp_sum
            BinaryConstraint(
                (temp_sum, carry_out),
                lambda t, c: c == (1 if t >= 10 else 0)
            )
        ])
    
    def _add_single_digit_column_constraints(self, d, d3, carry_in, carry_out, sum_var, col_idx):
        # Create temporary sum variable
        temp_sum = f'TEMP{col_idx}'
        self.variables.append(temp_sum)
        self.domains[temp_sum] = set(range(10))
        
        self.constraints.extend([
            # d = temp_sum
            BinaryConstraint(
                (d, temp_sum),
                lambda x, t: x == t
            ),
            
            # temp_sum + carry_in = sum_var + 10*carry_out
            BinaryConstraint(
                (temp_sum, carry_in),
                lambda t, c: any(
                    t + c == s + 10 * co
                    for s in self.domains[sum_var]
                    for co in self.domains[carry_out]
                )
            ),
            
            # sum_var should equal d3
            BinaryConstraint(
                (sum_var, d3),
                lambda s, r: s == r
            ),
            
            # Set carry_out based on temp_sum
            BinaryConstraint(
                (temp_sum, carry_out),
                lambda t, c: c == (1 if t >= 10 else 0)
            )
        ])

    def _add_carry_only_constraints(self, carry_in, carry_out):
        self.constraints.append(
            BinaryConstraint((carry_in, carry_out),
                lambda c_in, c_out: c_in == c_out)
        )

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())