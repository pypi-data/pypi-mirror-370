from ..errors.errors import InputError

def parseRule(rule:str)->str:
    """Parses a rule to ensure it has a valid format

    Args:
        rule (str): Rule to parse

    Raises:
        InputError: Can't find /
    Returns:
        str: Validated rule string
    """

    if (rule.find("/")==-1):
        raise InputError("Can't find /")

    arguements = rule.split("/")
    arguements = [i.strip() for i in arguements]

    if (arguements[0]==""):
        rule = arguements[1]
    elif (arguements[1]==""):
        # Don't think this really makes sense, because then you dont have a conclusion
        rule = arguements[0]

    return rule


# List of valid characters
validCharacters = ["#","@","->","<->","#'","@'","&",
                   "|","~","0","1","/","<=","&'","=>",",","<'"]


def checkIfNoTextAfterCharacter(string:str,character:str)->bool:
    """Checks if there is text after a certain character in a string

    Args:
        string (str): string to check
        character (str): character to check after

    Returns:
        bool: If text found, return true, otherwise false
    """
    if character not in string:
        return True
    parts = string.split(character,1)
    return len(parts)>1 and not parts[1]


def checkIfNoTextBeforeCharacter(string:str,character:str)->bool:
    """Checks if there is text before a certain character in a string

    Args:
        string (str): string to check
        character (str): character to check before

    Returns:
        bool: If text found, return true, otherwise false
    """
    if character not in string:
        return True
    parts = string.split(character,1)
    return len(parts)>1 and not parts[0]


def checkIfValidCharacters(rule:str)->bool:
    """Check if a rule does not have invalid characters. Invalid characters are ones that are
    found in the validCharacters list above. letters are valid.

    Args:
        rule (str): Rule to check

    Raises:
        InputError: Invalid character found at an index

    Returns:
        bool: True if all characters are valid
    """
    idx = 0
    while idx<len(rule):
        matched = False
        for symbol in validCharacters:
            if rule[idx:idx+len(symbol)]==symbol:
                idx += len(symbol)
                matched=True
                break
                
        if not matched:
            if (rule[idx].isalpha()):
                idx+=1
            else:
                if idx==len(rule):
                    raise InputError(f"Invalid character found at index {idx}: {rule[:idx]}<<{rule[idx:]}>>", errors="Invalid character")
                else:
                    raise InputError(f"Invalid character {rule[idx]} found at index {idx}: {rule[:idx]}<<{rule[idx]}>>{rule[idx+1:]}", errors="Invalid character")

    return True


# TODO : CHECK THAT LOGICAL CONNECTIVES ACTUALLY MAKE SENSE. eg) 
# TODO : CHECK MODAL COMPLEXITY 1
def preprocess(rule:str)->bool:
    """Check the conditions for potential errors in rule string

    Args:
        rule (str): Rule to check

    Raises:
        InputError: Formula needs a /
        InputError: No conclusion
        InputError: No premise
        InputError: Invalid characters present

    Returns:
        bool: True if the formula is valid
    """
    try:
        if (rule.count("/")!=1):
            raise InputError("Formula needs a /",errors="Formula syntax error")
        elif checkIfNoTextAfterCharacter(rule,"/"):
            raise InputError("No conclusion",errors="Formula syntax error")
        elif checkIfNoTextBeforeCharacter(rule,"/"):
            raise InputError("No premise",errors="Formula syntax error")
        
        checkIfValidCharacters(rule)
    except InputError as e:
        print(f"Error in formula {rule}:\nMessage:{e.message}\nError:{e.errors}")
        return False

    return True

