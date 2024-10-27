from typing import Tuple, List

DechiperResult = Tuple[str, int, int]

def caesar_shift_char(char: str, shift: int) -> str:
    # note i know that all texts only small letters but i will make it general in case its capital letter
    if char.isalpha():
        shift_base = ord('a') if char.islower() else ord('A')
        return chr((ord(char) - shift_base - shift) % 26 + shift_base)
    return char

def caesar_dechiper(ciphered: str, dictionary: List[str]) -> DechiperResult:
    '''
        This function takes the ciphered text (string)  and the dictionary (a list of strings where each string is a word).
        It should return a DechiperResult with the deciphered text, the cipher shift, 
        and the number of deciphered words that are not in the dictionary. 
    '''
    
    dictionary_set = set(dictionary) 
    MinnotInDict = float('inf')
    BestdecipherText = ""
    BestShift = 0
    words = ciphered.split()

    for shift in range(26):
        decipherText = []
        notInDict = 0
       

        for word in words:
            deciphered_word = ''.join(caesar_shift_char(char, shift) for char in word)
            
            if deciphered_word not in dictionary_set:
                notInDict += 1

            decipherText.append(deciphered_word)

        deciphered_text_str = ' '.join(decipherText)

       # print(f"Shift: {shift}, Not in Dictionary: {notInDict}, Deciphered Text: {deciphered_text_str}")

        if notInDict < MinnotInDict:
            MinnotInDict = notInDict
            BestdecipherText = deciphered_text_str
            BestShift = shift
    
   # print(f"Best Deciphered Text: {BestdecipherText}, Best Shift: {BestShift}, Min Not in Dictionary: {MinnotInDict}")

    return (BestdecipherText, BestShift, MinnotInDict)
