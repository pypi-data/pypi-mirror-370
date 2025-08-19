import re
from ..core.nomial import checkNominal,getNominals
from ..core.text_functions import replaceCharactersNoParen,checkOperator
from typing import Tuple

def getEqualities(text:str)->list[str]:
    matches = re.findall(r'\b[uwv]_\d+=\b[uwv]_\d+', text)
    return matches


def getNumbersFromString(text:str)->list[str]:
    numbers = re.findall(r'\d+', text)
    return numbers


def getRelations(text:str)->list[str]:
    matches = re.findall(r'\b[R|f]\([^()]*\)', text)
    return matches


def getQuantifiers(text:str)->list[str]:
    matches = re.findall(r'\b[F|E]\([^()]*\)', text)
    return matches


def getSubsetRelationSimplify(text:str)->list[str]:
    pattern = r'R\([^,]+,(\w+)\)\[R\([^,]+,\1\)'
    matches = [m.group(0) for m in re.finditer(pattern, text)]
    return matches


def extractSubsetArguements(text:str)->list[str]:
    pattern = r'R\(([^,]+),(\w+)\)\[R\(([^,]+),\2\)'
    output = []
    for match in re.finditer(pattern, text):
        a = match.group(1)
        b = match.group(2)  # common part
        c = match.group(3)

        output = [a,c,b]

    return output


def getLowerNominals(text:str)->str:
    if text.find("=")==-1:
        raise ValueError(f"Cannot find = in {text}")
    
    nominals = text.split("=")

    for nom in nominals:
        if (not checkNominal(nom)):
            raise ValueError(f"String is not a nominal:{nom}")
        
    validNominals = ["w","v"]

    for nom in validNominals:
        if ((nom in nominals[0] and nom not in nominals[1]) or
            (nom in nominals[1] and nom not in nominals[0])):
            raise ValueError(f"Mismatched nominals:{nominals[0]},{nominals[1]}")
    
    firstNomNumber = getNumbersFromString(nominals[0])
    secondNomNumber = getNumbersFromString(nominals[1])

    if (firstNomNumber>secondNomNumber):
        return nominals[1]
    else:
        return nominals[0]


def getSubstitutions(equations:list[str])->dict:
    substitutions = {}

    for equation in equations:
        try:
            lowerNom = getLowerNominals(equation)
            noms = equation.split("=")

            if noms[0]==lowerNom:
                substitutions[noms[1]]=lowerNom
            else:
                substitutions[noms[0]]=lowerNom
        except ValueError as e:
            raise ValueError(e)
        
    return substitutions
    

def removeEqualitiesAndOperator(condition:str,equations:list[str])->str:
    for e in equations:
        toErase = ""

        start = condition.find(e)
        # print(condition[condition.find(e):condition.find(e)+len(e)])
        symbolToTheLeft = ""
        symbolToTheRight = ""

        if (start-1>0):
            symbolToTheLeft = condition[start-1]
        if (start+len(e)+1<len(condition)):
            symbolToTheRight = condition[start+len(e)]
        
        if checkOperator(symbolToTheLeft):
            # print(f"Found Left:{symbolToTheLeft}")
            toErase = condition[start-1:start+len(e)]
            # print(toErase)
            
        elif checkOperator(symbolToTheRight):
            # print(f"Found Right:{symbolToTheRight}")
            toErase = condition[start:start+len(e)+1]
            # print(toErase)
        
        condition = condition.replace(toErase,"")
    
    return condition


def fixParentheses(text: str) -> str:
    depth = 0
    trimmed = list(text)

    for char in text:
        if char == '(':
            depth += 1
        elif char == ')':
            if depth > 0:
                depth -= 1
            else:
                # Unmatched closing bracket (early)
                pass

    # Remove unmatched closing brackets at the end
    while depth < 0 and trimmed and trimmed[-1] == ')':
        trimmed.pop()
        depth += 1

    # If there are extra closing brackets (but matched), just strip them from the end
    while trimmed and trimmed[-1] == ')':
        # Check if the current ending ')' has a matching '('
        temp_depth = 0
        for c in trimmed:
            if c == '(':
                temp_depth += 1
            elif c == ')':
                temp_depth -= 1
        if temp_depth >= 0:
            break  # All matched
        trimmed.pop()

    return ''.join(trimmed)


def removeQuanifiers(condition:str,substitutions:dict)->str:
    quantifiers = getQuantifiers(condition)

    for quan in quantifiers:
        nominal = getNominals(quan)[0]
        toErase = ""

        if nominal in list(substitutions.keys()):
            toErase = quan + "("
        
        condition = condition.replace(toErase,"")

    return condition


def finalSimplifications(condition:str)->Tuple[str,str]:
    subsets = getSubsetRelationSimplify(condition)

    matchedPart = ""

    for subset in subsets:
        subsetArgs = extractSubsetArguements(subset)
        #? is subset symbol
        matchedPart = subsetArgs[2]
        replaceString = f"R({subsetArgs[0]})?R({subsetArgs[1]})"
        condition = condition.replace(subset,replaceString)
    
    return condition,matchedPart


def simplifyConditon(condition:str)->str:
    condition = replaceCharactersNoParen(condition)
    eqns = getEqualities(condition)

    try:
        substitutions = getSubstitutions(eqns)
    except ValueError as e:
        print(e)
        return condition
    
    # print(substitutions)

    relations = getRelations(condition)

    for rel in relations:
        copyOfRel = rel

        for k,v in substitutions.items():
            rel = rel.replace(k,v)

        condition = condition.replace(copyOfRel,rel)
    
    condition = removeEqualitiesAndOperator(condition,eqns)

    condition = removeQuanifiers(condition,substitutions)
    condition,matchedPart = finalSimplifications(condition)
    matchedDict = {v:"" for v in [matchedPart]}

    condition = removeQuanifiers(condition,matchedDict)
    condition = fixParentheses(condition)

    condition = replaceCharactersNoParen(condition,True)
    return condition


if __name__=="__main__":
    condi = "w_0=w_1->F(v_0)(R(w_1,v_0)->E(w_2)(f(w_2)=v_0&F(v_1)(R(w_2,v_1)->E(w_3)(R(w_3,v_1)^w_3=w_0))))"
    res = simplifyConditon(condi)
    print(res)