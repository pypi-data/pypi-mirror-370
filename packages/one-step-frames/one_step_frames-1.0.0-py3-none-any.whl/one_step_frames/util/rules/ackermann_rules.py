import re


def findVariables(formula:str):
    """Find all variables in a given formula.
    Args:
        formula (str): The formula to search for variables.
    Returns:
        set: A set of variables found in the formula.
    """
    # Matches single lowercase letters that are not 'u', 'v', 'w', or 'i'
    matches = re.findall(r"\b(?![uvwi])([a-z])\b", formula)
    variables = set(matches)
    return variables


def checkPolarity(formula:str,varable:str)->bool|None:
    """Check the polarity of a variable in a formula.

    Args:
        formula (str): The formula to check.
        varable (str): The variable to check the polarity of.

    Returns:
        None|bool: Returns true if polarity is positive, false if negative, 
        and None if the variable is not found/not valid.
    """
    
    if varable not in formula or formula.find("<")==-1:
        return None
    
    splitParts = formula.split("<")

    if (len(splitParts)!=2):
        return None

    if splitParts[0].find(varable)!=-1:
        return False
    else:
        return True 


def ackermannHeuristic(formula:str,totalNumberVariables:int=-1):
    """Calculate the Ackermann heuristic for a given formula.
    If no => -> get -2, if varaibles eliminated, return the number of variables eliminated -2.
    Checks both version of the Ackermann rule.
    +1 if the variable is in the antecedent, +1 if the variable is not in the consequent, and 
    +1 if the polarity is negative.
    +1 if the variable is in the consequent, +1 if the variable is not in the antecedent, and 
    +1 if the polarity is positive.

    Args:
        formula (str): The formula to evaluate.
        totalNumberVariables (int, optional): The total number of variables in the formula. Defaults
        to -1

    Returns:
        int: The score based on the Ackermann heuristic.
    """

    if (formula.find("=>")==-1):
        checkNumberVariablesElim = totalNumberVariables-len(findVariables(formula))
        if (checkNumberVariablesElim>0):
            return checkNumberVariablesElim-2
        return -2
    
    score = 0
    variables = findVariables(formula)
    arguments = formula.split("=>")

    if (len(arguments)!=2):
        return -1
    
    gamma = arguments[0]
    delta = arguments[1]

    gamma_args = gamma.split("<")

    if (gamma_args[0] in variables):
        score+=1

        if (gamma_args[1].find(gamma_args[0])==-1):
            score+=1

        polarity = checkPolarity(delta,gamma_args[0])

        if (polarity==None):
            #what i do here xd
            return score
        elif (polarity==False):
            score+=1

    elif (gamma_args[1] in variables):
        score+=1
        if (gamma_args[0].find(gamma_args[1])==-1):
            score+=1

        polarity = checkPolarity(delta,gamma_args[1])

        if (polarity==None):
            #what i do here xd
            return score
        elif (polarity==True):
            score+=1
        #polarity now
    else:
        return 0
    
    return score


def checkAckermannConditions(formula: str, var: str) -> tuple[bool, int]:
    """Check if the Ackermann rule can be applied to a given formula with a specific variable.
    Args:
        formula (str): The formula to check.
        var (str): The variable to check.
    Returns:
        tuple: A tuple containing a boolean indicating if the rule can be applied and an integer
        indicating the rule index (0 or 1) if applicable, or -1 if not applicable.
    """
    if (formula.find("=>")==1):
        return (False,-1)
    
    splitArgs = formula.split("=>")

    if (len(splitArgs)!=2):
        return (False,-1)
    
    gamma,delta = splitArgs[0],splitArgs[1]
    gamma_args = gamma.split("<")
    antecedent,consequent = gamma_args[0],gamma_args[1]

    if len(gamma_args)!=2:
        return (False,-1)
    
    if var in antecedent:
        # x<phi=>delta
        if consequent.find(var)!=-1 or antecedent!=var:
            return (False,-1)
        
        polarity = checkPolarity(delta,var)

        if (polarity==None):
            #idk what to here xd
            return (False,-1)
        elif (polarity==False):
            return (True,1)
    elif var in consequent:
        # phi<x=>delta
        if antecedent.find(var)!=-1 or consequent!=var:
            return (False,-1)
        
        polarity = checkPolarity(delta,var)

        if (polarity==None):
            #idk what to here xd
            return (False,-1)
        elif (polarity==True):
            return (True,0)

    return (False,-1)


def applyAckermannRule(formula:str)->str:
    """Apply the Ackermann rule to a given formula.
    Args:
        formula (str): The formula to apply the Ackermann rule to.
    Returns:
        str: The modified formula after applying the Ackermann rule, or the original formula if
        Ackermann rule cannot be applied.
    """
    varaibles = findVariables(formula)
    
    for var in varaibles:
        ackermannApplicable = checkAckermannConditions(formula,var)
        canApply = ackermannApplicable[0]
        rule = ackermannApplicable[1]

        if (not canApply):
            continue
        
        splitFormula = formula.split("=>")
        gamma,delta = splitFormula[0],splitFormula[1]

        if (canApply):
            phi = gamma.split("<")[rule]
            delta = delta.replace(var,phi)
            return f"{delta}"

    return formula
