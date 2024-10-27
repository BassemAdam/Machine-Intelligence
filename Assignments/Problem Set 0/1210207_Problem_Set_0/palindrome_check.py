def palindrome_check(string: str) -> bool:
    '''
    This function takes a string and returns whether the string is a palindrome or not.
    A palindrome is a string that does not change if read from left to right or from right to left.
    Assume that empty strings are palindromes.
    '''
    if string == "":
        return True
    
    return string == string[::-1]
print(palindrome_check("racecar")) # True