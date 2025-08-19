from .text_functions import replaceCharacters

# Make the dynamic mapping
def get_letter(index):
    char_code = 97 + index

    # Skip 'i', 'v', and 'w'
    skipCharacters = ["i","v","w","u","f"]
    
    skips = {ord(i) for i in skipCharacters}

    while char_code in skips:
        char_code += 1

    # If passed 'z', wrap to 'A', skipping again if needed
    if char_code > ord('z'):
        char_code = 65 + (index - 25)  # Adjust for overflow beyond 'z'
        while char_code in skips:
            char_code += 1

    return chr(char_code)


def generateMapping():
    nominalToSymbol = {}

    # w_0 to w_8 → 'a' to 'h', skip 'i' → 'j' instead
    for i in range(9):
        nominalToSymbol[f"w_{i}"] = get_letter(i)

    # v_0 to v_8 → continue after 'j', total offset of 9
    for i in range(9):
        nominalToSymbol[f"v_{i}"] = get_letter(i + 9)

    # u_0 to u_8 → continue again
    for i in range(9):
        nominalToSymbol[f"u_{i}"] = get_letter(i + 18)

    return nominalToSymbol


def replaceNominals(formula:str,nominalToSymbol:dict=generateMapping(),reverse:bool=False):
    if not reverse:
        for k,v in nominalToSymbol.items():
            formula = formula.replace(k,v)
    else:
        reversedMap = {v:k for k,v in nominalToSymbol.items()}

        for k,v in reversedMap.items():
            formula = formula.replace(k,v)

    return formula


def cleanUp(formula):
    formula = replaceCharacters(formula,True)
    formula = replaceNominals(formula,reverse=True)
    return formula.replace("{}","")
