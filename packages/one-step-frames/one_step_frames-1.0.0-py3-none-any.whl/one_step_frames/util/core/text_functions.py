import re

# Operator/operand functonality
operator_map = {
    "<->": "+",
    "=>": ">",
    "->": "[",
    "<": "<",
    "<'": "]",
    "#'": "$",
    "#": "#",
    "@'": "%",
    "@": "@",
    "~": "~",
    "i*": "*",
    "i!": "!",
    "i": "i",
    "^": "^",
    "|": "|",
    "&": "&"
}

def checkOperand(token:str)->bool:
    return bool(re.fullmatch(r"[a-hj-zA-HJ-Z]", token))

def checkOperator(token: str) -> bool:
    """Check if a token is a valid operator.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is a valid operator, otherwise False.
    """
    return bool(re.fullmatch(r"i|[=><\[\]\#\$\@\%\~\*\!\^|&]", token))



# Text replacement
def replaceCharacters(formula: str,reverse:bool=False) -> str:
    if not reverse:
        for i, j in operator_map.items():
            formula = formula.replace(i, j)
        
        formula = formula.replace("(", "")
        formula = formula.replace(")", "")
    else:
        reverse_operator_map = {v: k for k, v in operator_map.items()}
        for i, j in reverse_operator_map.items():
            formula = formula.replace(i, j)

        unary_ops = ["i*", "i!", "i"]
        unary_syms = [operator_map[op] for op in unary_ops]

        prev = None
        while formula != prev:
            prev = formula
            # Add parentheses around non-parenthesized operand
            formula = re.sub(
                rf"({'|'.join(map(re.escape, unary_syms))})(?!\s*\()([a-zA-Z][a-zA-Z0-9_]*)",
                r"\1(\2)",
                formula
            )

    return formula


def replaceCharactersNoParen(formula: str,reverse:bool=False) -> str:
    if not reverse:
        for i, j in operator_map.items():
            formula = formula.replace(i, j)
        
        # formula = formula.replace("(", "")
        # formula = formula.replace(")", "")
    else:
        reverse_operator_map = {v: k for k, v in operator_map.items()}
        for i, j in reverse_operator_map.items():
            formula = formula.replace(i, j)

        unary_ops = ["i*", "i!", "i"]
        unary_syms = [operator_map[op] for op in unary_ops]

        prev = None
        while formula != prev:
            prev = formula
            # Add parentheses around non-parenthesized operand
            formula = re.sub(
                rf"({'|'.join(map(re.escape, unary_syms))})(?!\s*\()([a-zA-Z][a-zA-Z0-9_]*)",
                r"\1(\2)",
                formula
            )

    return formula
