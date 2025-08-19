import re
from ...AST.core.abstract_syntax_tree import AbstractSyntaxTree
from ...AST.core.ast_util import getLeafNodes,toInfix

modalOperators = ["#","@","#'","@'"]
#TODO add <-> if needed
logicConnectives = ["=>","<","<'","#","#'","@","@'","~","i*","i!","i","^","|","&","->","<->"]


def findAtomicFormulas(formula:str,additionalConnectives:list[str]=[])->list[str]:
    """Given some formula, it returns all the atomic formulas
    in order. Given #x&x, it returns [#x,x]

    Args:
        formula (str): formula to split

    Returns:
        list[str]: list of atomic formulas in order
    """
    symbols = None
    if additionalConnectives==[]:
        symbols = logicConnectives
    else:
        additionalConnectives.extend(logicConnectives)
        symbols = additionalConnectives.copy()

    delimiters = f'[{"".join(symbols)}]'
    subformulasAntecdent = re.split(delimiters,formula)

    # Remove empty strings from the list
    subformulasAntecdent = [subformula for subformula in subformulasAntecdent if subformula.strip()]
    
    return subformulasAntecdent


def getConnectives(formula:str,additionalConnectives:list[str]=[])->list[str]:
    """Given some formula, it returns all the connectives used in order.
    Given #x&x|y, it returns [&,|]

    Args:
        formula (str): formula to split

    Returns:
        list[str]: list of logical connectives in order
    """
    symbols = None
    if additionalConnectives==[]:
        symbols = logicConnectives
    else:
        additionalConnectives.extend(logicConnectives)
        symbols = additionalConnectives.copy()

    symbols = sorted(symbols, key=len, reverse=True)
    delimiters = f"(?:{'|'.join(map(re.escape,symbols))})"
    connectives = re.findall(delimiters,formula)
    return connectives


def getVariable(formula:str)->list[str]:
    """Given some formula, it returns all the propositional variables"""
    outputList = []
    for i in formula:
        if i.isalpha() and i!="i" and i not in modalOperators:
            outputList.append(i)
    return outputList


def checkIfFree(atomicFormula:str)->bool:
    """Given some atomic formula, it checks if the variable is free.
    Example:#x -> NOT FREE,x -> FREE. 
    It works by first finding the propositional variable,
    then checking if it has some modal operator connected to it. 

    Args:
        atomicFormula (str): atomic formula to check

    Returns:
        bool: True if free, otherwise False
    """
    propIdx = -1

    for i,j in enumerate(atomicFormula):
        if j.isalpha():
            propIdx = i

        if (propIdx!=-1):
            break
    
    temp = propIdx

    while (temp>=0):
        if atomicFormula[temp] in modalOperators:
            return False
        temp-=1

    return True


def initAtomicFormula(formula:str)->str:
    """Initializes an atomic formula. If it is free, then it puts a 
    nominial with it, otherwise leaves as is.

    Args:
        formula (str): atomic formula

    Returns:
        str: initialized formula
    """
    isFree = checkIfFree(formula)

    if (isFree):
        return f"i({formula})"
    else:
        return formula


def initFormula(subformula:str)->str:
    """Initializes a formula by doing the following:
    1. Replacing '/' with '=>'
    2. Replacing '->' with '<'
    3. Building an abstract syntax tree from the formula
    4. Replacing all leaf nodes with parents that arent modal operators
    with an initialized atomic formula(putting morphism i() around it)

    Args:
        subformula (str): subformula to initialize

    Returns:
        str: initialized formula
    """
    subformula = subformula.replace("/","=>")
    subformula = subformula.replace("->","<")
    ast = AbstractSyntaxTree()
    ast.buildTree(subformula)
    # Get leaf nodes and their parents
    if (ast.root is None):
        return subformula
    
    leafAndParents = getLeafNodes(ast.root,None,[])
    for i in leafAndParents:
        if i[1]==None:
            #Must be root
            parentValue = ""
        else:
            parentValue = i[1].value
        
        childValue = i[0].value
        if (parentValue not in modalOperators):
            res = initAtomicFormula(childValue)
            i[0].value = res

    return toInfix(ast.root)
