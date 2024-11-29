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

        # Setup variables and domains please go inside of them i will explain it more there 
        # Define Variables 
        problem._initialize_variables(LHS0, LHS1, RHS)
        # Define Domains
        problem._initialize_domains()
        
        # Add constraints
        # check that the letters are all different
        problem._add_all_different_constraints()
        # check that the sum of the letters is equal to the sum of the letters in the result
        problem._add_column_constraints()
        
        return problem

    def _initialize_variables(self, LHS0: str, LHS1: str, RHS: str) -> None:
        # note self here is a CryptArithmeticProblem object its like this in cpp
        # the input given to this function will be for ex: LH0 = "SEND", LHS1 = "MORE", RHS = "MONEY" 
        # Get unique letters and calculate lengths
        self.letters = set(LHS0 + LHS1 + RHS) # why did we use set ?? simply to get unique letters set have no duplicates
        self.max_len = max(len(LHS0), len(LHS1), len(RHS)) # get the max length of the 3 terms so that i can pad the other terms with zeros to be exactly above each other 
        
        # Pad terms for alignment
        # we will use rjust to get that behaviour its a string method i got it from internet that right justifiy within a specified length given a specified 
        # character if the string is less than the specified length it will add the specified character to the left of the string until it reaches the specified length
        # so now our LHS0, LHS1, RHS will be padded with zeros to be exactly above each other 
        # 0SEND 
        # 0MORE
        # MONEY
        self.LHS0_padded = LHS0.rjust(self.max_len, '0')
        self.LHS1_padded = LHS1.rjust(self.max_len, '0')
        self.RHS_padded = RHS.rjust(self.max_len, '0')
        
        # Create auxiliary variables FOR CARRY AND SUM
        #  c4 c3 c2 c1 c0
        #  0  S  E  N  D 
        #  0  M  O  R  E
        #  M  O  N  E  Y
        #  s4 s3 s2 s1 s0
        self.carries = [f'C{i}' for i in range(self.max_len)]
        self.sums = [f'SUM{i}' for i in range(self.max_len)]
        
        # Set all variables
        self.variables = list(self.letters) + self.carries + self.sums

        # # Debug print statements
        # red = "\033[91m"
        # reset = "\033[0m"
        # print(f"{red}Letters: {self.letters}{reset}")
        # print(f"{red}Max Length: {self.max_len}{reset}")
        # print(f"{red}LHS0 Padded: {self.LHS0_padded}{reset}")
        # print(f"{red}LHS1 Padded: {self.LHS1_padded}{reset}")
        # print(f"{red}RHS Padded: {self.RHS_padded}{reset}")
        # print(f"{red}Carries: {self.carries}{reset}")
        # print(f"{red}Sums: {self.sums}{reset}")
        # print(f"{red}All Variables: {self.variables}{reset}")

    def _initialize_domains(self) -> None:

        self.domains = {}   

        # Get actual first letters (not padded)
        LHS0_first = self.LHS[0][0]  # First letter of first term (e.g., P from POINT)
        LHS1_first = self.LHS[1][0]  # First letter of second term (e.g., Z from ZERO)
        RHS_first = self.RHS[0]      # First letter of result (e.g., E from ENERGY)
        
        # Leading letters cannot be zero
        leading_letters = {LHS0_first, LHS1_first, RHS_first}
        
        # Set domains for letters
        # we will use function range which generates a sequence of numbers 0 1 2 3 for example 
        # and set which converts the sequence to a set
        for letter in self.letters:
            # Leading letters get domain [1-9], others [0-9]
            self.domains[letter] = set(range(1, 10)) if letter in leading_letters else set(range(10))
        
        # Carry domains
        for carry in self.carries:
            self.domains[carry] = {0, 1}
        
        # Sum domains
        for sum_var in self.sums:
            self.domains[sum_var] = set(range(10))
        
        # to see the set for every letter uncomment this part 
        # # Debug print statements 
        # blue = "\033[94m"
        # reset = "\033[0m"
        # for var, domain in self.domains.items():
        #     print(f"{blue}{var}: {domain}{reset}")

    def _add_all_different_constraints(self) -> None:
        # Initialize constraints list for cryptographic problem
        self.constraints = []

        # we defined above the letters as set now we want to iterate overthem so we will convert them to list
        letter_list = list(self.letters)
        
        for i in range(len(letter_list)): # iterate over the letters
            for j in range(i + 1, len(letter_list)): 
                # iterate over the letters starting from the next 
                # letter since we dont want to compare the same letter with 
                # itself and we dont want to compare the same pair twice thats why its starting with i+1
                # we will add a binary constraint to the constraints list
                # the binary constraint takes names of variables that have that constrained 
                # and a function that takes the values of the variables 
                self.constraints.append(
                    BinaryConstraint(
                        (letter_list[i], letter_list[j]),
                        lambda x, y: x != y
                    )
                )

    def _add_column_constraints(self) -> None:
        # this method should arithmetic relationships between the columns of the cryptarithmetic problem
        # we will iterate over the columns and add constraints for each column
        # note i will give examples of whats happening here based on the example above of 0send 0more money 
        for i in range(self.max_len): # first coloumn will be D E Y
            # get the position of the column from the right
            # think about this as black box and then press on the function and i will explain 
            # more inside of it how we add single column constraints
            pos = self.max_len - i - 1 # max length is 5 so the first column will be 5-0-1 = 4 
            # note we consider 0 also so range from 0 to 4
            digits = self._get_column_digits(pos) # get the digits of the column D E Y
            self._add_single_column_constraints(i, digits) # add the constraints for the column with those digits

    def _get_column_digits(self, pos: int) -> tuple:
        # Get the digits of the column at the given position
        d1 = self.LHS0_padded[pos] 
        d2 = self.LHS1_padded[pos] 
        d3 = self.RHS_padded[pos]

        # Debug print statements
        blue = "\033[94m"
        reset = "\033[0m"
        print(f"{blue}Column position: {pos}{reset}")
        print(f"{blue}LHS0 digit: {d1}{reset}")
        print(f"{blue}LHS1 digit: {d2}{reset}")
        print(f"{blue}RHS digit: {d3}{reset}")

        return d1, d2, d3

    def _add_single_column_constraints(self, col_idx: int, digits: tuple) -> None:
        d1, d2, d3 = digits # unpack the digits of the column
        carry_in = self.carries[col_idx] # get the carry in variable of the column
        carry_out = self.carries[col_idx] #etc... just getting the associated variables to that coloumn
        sum_var = self.sums[col_idx]
        
        if d1 and d2: # if both digits are not None in case of D E Y 
            self._add_two_digit_column_constraints(d1, d2, d3, carry_in, carry_out, sum_var, col_idx)
        # note if i d1 does not exist or d2 or maybe both it depends on the length of words in left and right side if any case of those i would need to handle it 
        # in cases like that bellow HOWEVER above i have handled that case by padding and added '0' to the left of the word to make them equal in length
        # elif d1: # if only one digit is not None maybe some words have 4 letters and some have 5 so we need to handle that
        #     self._add_two_digit_column_constraints(d1, '0', d3, carry_in, carry_out, sum_var, col_idx)
        # elif d2: # same as above
        #     self._add_two_digit_column_constraints('0', d2, d3, carry_in, carry_out, sum_var, col_idx)
        # else:
        #     self._add_two_digit_column_constraints('0', '0', d3, carry_in, carry_out, sum_var, col_idx)
                                                      
    def _add_two_digit_column_constraints(self, digit1, digit2, result_digit, carry_in, carry_out, sum_var, col_idx):
        
        # Define Lsum  represents digit1 + digit2  + carry_in
        Lsum = f'L_SUM{col_idx}'
        self.variables.append(Lsum)
        self.domains[Lsum] = set(range(0,200))  # Max possible sum is 991 because i will concatinate values of d1 and d2 
        
        # Define Rsum  represents sum_var + 10*carry_out
        Rsum = f'R_SUM{col_idx}'
        self.variables.append(Rsum)
        self.domains[Rsum] = set(range(0,20)) 

     


        def split_number(num): # left to right 0 to last length
            digits = [int(d) for d in str(num)]
            return digits
        def safe_get(lst, index, default=0):
            try:
                return lst[index]
            except IndexError:
                return default

        self.constraints.extend([
            # Constraint 1: Lsum = Rsum and i dont need to convert them to integers here
            BinaryConstraint( # 199 => 1 + 9 + 9 =  RHG = 9 + 10*1 
                (Lsum, Rsum),
                lambda Lsum, Rsum: sum(split_number(Lsum)) == sum(split_number(Rsum))
            ),
             # Constraint 2: Make sure that Lsum first digit is equal to digit1 since its string 
             # so i will split and convert to integer and then check if its equal to digit1
             # i will use the function int to convert the string to integer
             # Constraint 2: Lsum's first digit equals digit1
            BinaryConstraint(
                (Lsum, digit1),
                lambda Lsum, digit1: safe_get(split_number(Lsum),2) == int(digit1)
            ),
            # Constraint 3: Lsum's second digit equals digit2
            BinaryConstraint(
                (Lsum, digit2),
                lambda Lsum, digit2: safe_get(split_number(Lsum),1) == int(digit2)
            ),
              BinaryConstraint(
                (Lsum, carry_in),
                lambda Lsum, carry_in: carry_in == safe_get(split_number(Lsum),0)
            ),
            # Constraint 4: Rsum's first digit equals carry_out
            BinaryConstraint(
                (Rsum, carry_out),
                lambda Rsum, carry_out: split_number(Rsum)[0] == int(carry_out)
            ),
            # Constraint 5: Rsum's second digit equals result_digit
            BinaryConstraint(
                (Rsum, result_digit),
                lambda Rsum, result_digit: safe_get(split_number(Rsum),1) == int(result_digit)
            ),
             
            # Constraint 5: Rsum's second digit equals result_digit
            BinaryConstraint(
                (Rsum, sum_var),
                lambda Rsum, sum_var: safe_get(split_number(Rsum),1) == int(sum_var)
            ),
            # Add special constraint for the last column
            BinaryConstraint(
                    (Rsum, carry_out),
                    lambda Rsum, cout: (
                        print('\n' + '='*50),
                        print('\033[95m[DEBUG] Constraint Evaluation\033[0m'),
                        print('\033[94m{:<20} {}\033[0m'.format('Rsum value:', Rsum)),
                        print('\033[94m{:<20} {}\033[0m'.format('value of R in col before last:', cout)),
                        print('\033[92m{:<20} {}\033[0m'.format('Rsum last digit:', safe_get(split_number(Rsum),1))),
                        print('\033[92m{:<20} {}\033[0m'.format('cout that comes from col before last:', cout)),
                        print('\033[93m{:<20} {}\033[0m'.format('Constraint check:', 
                            f'{safe_get(split_number(Rsum),1)} == {safe_get(split_number(cout),0)}')),
                        print('='*50 + '\n'),
                        safe_get(split_number(Rsum),1) == cout 
                    )
                ),
        ])
              
 
    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())