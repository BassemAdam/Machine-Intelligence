from typing import Tuple
import re
from CSP import Assignment, Problem, UnaryConstraint, BinaryConstraint

#TODO (Optional): Import any builtin library or define any helper function you want to use

def split_number(number: int) -> list:
    return [int(digit) for digit in str(number)]

def safeget(lst, index, default=0):
    """
    Safely get an element from a list at given index.
    
    Args:
        lst (list): Input list
        index (int): Index to retrieve
        default (Any): Default value if index out of bounds (default: 0)
    
    Returns:
        Any: Element at index if exists, else default value
    """
    try:
        return lst[index]
    except (IndexError, TypeError):
        return default

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
        # Read a cryptarithmetic puzzle from a file
    
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())
        
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
        self.variables = list(self.letters) + self.carries 
         
        self.Aux_variables = []  # Initialize empty list to store all aux vars
        
        # In the loop
        for col_idx in range(self.max_len):
            # Define Lsum represents digit1 + digit2 + carry_in
            Lsum = f'L_SUM{col_idx}'
            # Define Rsum represents sum_var + 10*carry_out
            Rsum = f'R_SUM{col_idx}'
            
            # Store pair for this column you can ignore it i was just using in debugging
            self.Aux_variables.append((Lsum, Rsum))
            
            # Add to main variables list
            self.variables.extend([Lsum, Rsum])
          

        #       # Debug print statements
        # red = "\033[91m"
        # pink = "\033[95m"
        # reset = "\033[0m"
        
        # print(f"\n{red}=== Basic Variables ==={reset}")
        # print(f"{red}Letters: {self.letters}{reset}")
        # print(f"{red}Max Length: {self.max_len}{reset}")
        # print(f"{red}LHS0 Padded: {self.LHS0_padded}{reset}")
        # print(f"{red}LHS1 Padded: {self.LHS1_padded}{reset}")
        # print(f"{red}RHS Padded: {self.RHS_padded}{reset}")
        # print(f"{red}Carries: {self.carries}{reset}")
        
        # print(f"\n{pink}=== Auxiliary Variables ==={reset}")
        # for col_idx, (lsum, rsum) in enumerate(self.Aux_variables):
        #     print(f"{pink}Column {col_idx}:{reset}")
        #     print(f"{pink}  Lsum: {lsum}{reset}")
        #     print(f"{pink}  Rsum: {rsum}{reset}")
        
        # print(f"\n{red}=== All Variables ==={reset}")
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
        
            
        for i, carry in enumerate(self.carries):
            if i == 0:  # First carry
                self.domains[carry] = {0} 
            else:  # All other carries
                self.domains[carry] = {0, 1} 
        
   
        for col_idx in range(self.max_len):
            # Define Lsum  represents digit1 + digit2  + carry_in
            Lsum = f'L_SUM{col_idx}'
            # Define Rsum  represents sum_var + 10*carry_out
            Rsum = f'R_SUM{col_idx}'
            self.domains[Lsum] = set(range(0,200))  # Max possible sum is 199 because i will concatinate values of cin and d1 and d2 
            self.domains[Rsum] = set(range(0,20)) 
         
      
         
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

        # # Debug print statements
        # blue = "\033[94m"
        # reset = "\033[0m"
        # print(f"{blue}Column position: {pos}{reset}")
        # print(f"{blue}LHS0 digit: {d1}{reset}")
        # print(f"{blue}LHS1 digit: {d2}{reset}")
        # print(f"{blue}RHS digit: {d3}{reset}")

        return d1, d2, d3

    def _add_single_column_constraints(self, col_idx: int, digits: tuple) -> None:
        d1, d2, d3 = digits # unpack the digits of the column

        def safe_get(lst, index, default=0):
            try:
                return lst[index]
            except IndexError:
                return default
        Lsum,Rsum = self.Aux_variables[col_idx]
        carry_in = self.carries[col_idx] # get the carry in variable of the column
        carry_out =safe_get(self.carries,col_idx+1,'C0')  #etc... just getting the associated variables to that coloumn last carry out will be 0 so i will set it to C0

        
        if d1 and d2: 
            self._add_two_digit_column_constraints(d1, d2, d3,Lsum,Rsum, carry_in, carry_out, col_idx)
        # note if i d1 does not exist or d2 or maybe both it depends on the length of words in left and right side if any case of those i would need to handle it 
        # in cases like that bellow HOWEVER above i have handled that case by padding and added '0' to the left of the word to make them equal in length
        # elif d1: # if only one digit is not None maybe some words have 4 letters and some have 5 so we need to handle that
        #     self._add_two_digit_column_constraints(d1, '0', d3, carry_in, carry_out, sum_var, col_idx)
        # elif d2: # same as above
        #     self._add_two_digit_column_constraints('0', d2, d3, carry_in, carry_out, sum_var, col_idx)
        # else:
        #     self._add_two_digit_column_constraints('0', '0', d3, carry_in, carry_out, sum_var, col_idx)
                                                      
    def _add_two_digit_column_constraints(self, digit1, digit2, result_digit, Lsum, Rsum, carry_in, carry_out, col_idx):
        """
        Adds constraints for a single column in a cryptarithmetic puzzle.

        Args:
            digit1 (str): First digit in the column (from LHS0).
            digit2 (str): Second digit in the column (from LHS1).
            result_digit (str): Result digit in the column (from RHS).
            Lsum (str): Auxiliary variable representing the left-side sum (digit1 + digit2 + carry_in).
            Rsum (str): Auxiliary variable representing the right-side sum (result_digit + 10 * carry_out).
            carry_in (str): Carry into the column.
            carry_out (str): Carry out of the column.
            col_idx (int): The column index (0-based, rightmost is 0).
        """
        # Handle padded zeros
        if digit1 == '0':
            self.variables.append(digit1)
            self.domains[digit1] = {0}
            
        if digit2 == '0':
            self.variables.append(digit2)
            self.domains[digit2] = {0}

        # Edge cases for carries
        if col_idx == 0:  # Rightmost column: carry_in must be 0
            self.constraints.append(
                UnaryConstraint(carry_in, lambda cin: cin == 0)
            )
        if col_idx == self.max_len - 1:  # Leftmost column: carry_out must be 0
            self.constraints.append(
                UnaryConstraint(carry_out, lambda cout: cout == 0)
            )

        # Constraint: Lsum = digit1 + digit2 + carry_in
        # nice note maybe Lsum will be only two digits or maybe one digit or maybe three digits so i will handle that by
        # using function safeget that i defined above to get the digit at the index if it exists if not return 0 and we are accessing them from right so we are matching digits correctly 
        self.constraints.append(
            BinaryConstraint(
                (Lsum, digit1),
                lambda lsum, d1: safeget(split_number(lsum),-1) == d1   # Ensure the last digit of Lsum matches digit1
            )
        )
        self.constraints.append(
            BinaryConstraint(
                (Lsum, digit2),
                lambda lsum, d2: safeget(split_number(lsum),-2) == d2   # Ensure the second last digit of Lsum matches digit2
            )
        )
        self.constraints.append(
            BinaryConstraint(
                (Lsum, carry_in),
                lambda lsum, cin: safeget(split_number(lsum),-3) == cin   # Ensure the third last digit of Lsum matches carry_in
            )
        )

        # Constraint: Rsum = result_digit + 10 * carry_out
        self.constraints.append(
            BinaryConstraint(
                (Rsum, result_digit),
                lambda rsum, rd: split_number(rsum)[-1] == rd  # Ensure the last digit of Rsum matches result_digit
            )
        )
        self.constraints.append(
            BinaryConstraint(
                (Rsum, carry_out),
                lambda rsum, cout: (
                    # For single digit Rsum, carry_out must be 0
                    # For two digits, carry_out must be first digit
                    (len(split_number(rsum)) == 1 and cout == 0) or
                    (len(split_number(rsum)) == 2 and split_number(rsum)[0] == cout)
                )
            )
        )
        # Constraint: Lsum = Rsum
        self.constraints.append(
            BinaryConstraint(
                    (Lsum, Rsum),
                    lambda Lsum, Rsum: (
                        sum(split_number(Lsum)) == 
                            split_number(Rsum)[-1] + 10 * safeget(split_number(Rsum),-2,0)
                
                    )
                ),
        )
