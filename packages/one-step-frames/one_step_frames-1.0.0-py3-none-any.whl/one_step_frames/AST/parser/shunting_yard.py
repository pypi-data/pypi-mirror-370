import re
from .nominal import Nominal

nominalManager = Nominal()

# Encodes the operators to a 1 character representation
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

# Maps operators to their associativity and precedence
# Associativity: "L" for left associative, "R" for right associative
# Precedence: Higher number means higher precedence
associativity_map = {
    ">": "R",   
    "=": "L",   
    "<": "L",
    "[": "L",   
    "#": "R",
    "$": "R",   
    "@": "R",
    "%": "R",   
    "~": "R",
    "*": "R",  
    "!": "R",   
    "i": "R",
    "^": "R",
    "|": "L",
    "&": "L",
    "]": "L" 
}

precedence_map = {
    ">": 1,    
    "=": 1,    
    "|": 2,
    "&": 2,
    "<": 3,
    "[": 3, 
    "^": 4,
    "]": 4,
    "#": 6,
    "$": 6,
    "@": 6,
    "%": 6,
    "~": 5,
    "*": 5,
    "!": 5,
    "i": 5
}

regexPatterns={
    "OPERATOR": r"i|[=><\[\]\#\$\@\%\~\*\!\^|&]",  # i operator alone first
    "OPERAND": r"[a-hj-zA-HJ-Z]",                  # operands single letter excluding 'i'
    "SKIP": r"\s+",
    "MISMATCH": r"."
}


def replaceCharacters(formula: str, reverse: bool = False) -> str:
    """Replace/Encode operators in a formula with their single-character representations 
    or revert them back.

    Args:
        formula (str): The formula to process, which may contain operators and operands.
        reverse (bool, optional): True=>Decodes the string, while False encodes it. Defaults to False.

    Returns:
        str: The processed formula with operators replaced by single characters or reverted back.
    """
    if not reverse:
        nominalManager.createMapping(formula)
        mapping = nominalManager.getMapping()

        for k,v in mapping.items():
            formula = formula.replace(k,v)

        for i, j in operator_map.items():
            formula = formula.replace(i, j)

        formula = formula.replace("(", "")
        formula = formula.replace(")", "")
    else:
        mapping = nominalManager.getMapping()
        reverseNominalMap = {v:k for k,v in mapping.items()}
        
        for i,j in reverseNominalMap.items():
            formula = formula.replace(i,j)

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


def tokenize(formula:str)-> list:
    """Tokenizes a formula into operators and operands.

    Args:
        formula (str): The formula to tokenize, which may contain operators and operands.

    Raises:
        RuntimeError: If an unexpected character is found in the formula or if there are unmatched parentheses.
        RuntimeError: If there are unexpected characters at the end of the input.

    Returns:
        list: A list of tokens extracted from the formula, 
        where each token is either an operator or an operand.
    """
    token_specification = [
        ("OPERATOR", regexPatterns["OPERATOR"]),  # i operator alone first
        ("OPERAND",  regexPatterns["OPERAND"]),                  # operands single letter excluding 'i'
        ("SKIP", regexPatterns["SKIP"]),
        ("MISMATCH", regexPatterns["MISMATCH"]),
    ]

    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    get_token = re.compile(tok_regex).match
    pos = 0
    tokens = []
    mo = get_token(formula, pos)
    while mo is not None:
        kind = mo.lastgroup
        value = mo.group()
        if kind == "SKIP":
            pass
        elif kind == "MISMATCH":
            raise RuntimeError(f"Unexpected character: {value} at pos {pos}")
        else:
            tokens.append(value)
        pos = mo.end()
        mo = get_token(formula, pos)
    if pos != len(formula):
        raise RuntimeError(f"Unexpected character at end of input: {formula[pos:]}")
    return tokens


def checkOperand(token: str) -> bool:
    """Check if a token is a valid operand.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is a valid operand, otherwise False.
    """
    return bool(re.fullmatch(regexPatterns["OPERAND"], token))


def checkOperator(token: str) -> bool:
    """Check if a token is a valid operator.

    Args:
        token (str): The token to check.

    Returns:
        bool: True if the token is a valid operator, otherwise False.
    """
    return bool(re.fullmatch(regexPatterns["OPERATOR"], token))


def shuntingYardAlgorithm(formula: str) -> str:
    """Main function to convert an infix formula to postfix notation using 
    the Shunting Yard algorithm.

    Args:
        formula (str): The infix formula to convert, which may contain operators and operands.

    Raises:
        RuntimeError: If an unknown token is encountered in the formula.

    Returns:
        str: The postfix notation of the input formula, where operators follow their operands.
    """
    output = ""
    operatorStack = []
    tokens = tokenize(formula)
    # print(tokens)
    
    # Based on your mappings, these are unary prefix operators
    unary_operators = {"#", "$", "@", "%", "~", "*", "!", "i"}
    
    for token in tokens:
        if checkOperand(token):
            output += token + " "
            # After an operand, pop any pending unary operators
            while operatorStack and operatorStack[-1] in unary_operators:
                output += operatorStack.pop() + " "
        elif token == '(':
            operatorStack.append(token)
        elif token == ')':
            while operatorStack and operatorStack[-1] != '(':
                output += operatorStack.pop() + " "
            operatorStack.pop()  # pop '('
        elif checkOperator(token):
            if token in unary_operators:
                # Unary operators - just push onto stack, will be popped after operand
                operatorStack.append(token)
            else:
                # Binary operators
                while (
                    operatorStack
                    and operatorStack[-1] != '('
                    and checkOperator(operatorStack[-1])
                    and (
                        (associativity_map[token] == "L" and precedence_map[token] <= precedence_map[operatorStack[-1]])
                        or
                        (associativity_map[token] == "R" and precedence_map[token] < precedence_map[operatorStack[-1]])
                    )
                ):
                    output += operatorStack.pop() + " "
                operatorStack.append(token)
        else:
            raise RuntimeError(f"Unknown token: {token}")
    
    while operatorStack:
        output += operatorStack.pop() + " "
    
    return output.strip()


def postfixToInfix(postfix_expr: str) -> str:
    """Convert a postfix expression to infix notation.
    This function takes a postfix expression as input and converts it to infix notation.

    Args:
        postfix_expr (str): The postfix expression to convert, which may contain operators and operands.

    Raises:
        RuntimeError: Not enough operands for unary operator: {token}
        RuntimeError: Not enough operands for operator: {token}
        RuntimeError: Unknown token in postfix: {token}
        RuntimeError: Invalid postfix expression: {postfix_expr}

    Returns:
        str: The infix notation of the input postfix expression, where operators are 
        placed between their operands.
    """
    tokens = postfix_expr.split()
    stack = []
    
    for token in tokens:
        if checkOperand(token):
            stack.append(token)
        elif checkOperator(token):
            unary_operators = {"#", "$", "@", "%", "~", "*", "!", "i"}
            if token in unary_operators:
                if len(stack) < 1:
                    raise RuntimeError(f"Not enough operands for unary operator: {token}")
                operand = stack.pop()
                if any(op in operand for op in [" => ", " -> ", " <-> ", " & ", " | ", " < ", " <' ", " ^ "]):
                    stack.append(f"{token}({operand})")
                else:
                    stack.append(f"{token}{operand}")
            elif len(stack) >= 2:
                # Binary operators
                right = stack.pop()
                left = stack.pop()
                stack.append(f"{left} {token} {right}")
            else:
                raise RuntimeError(f"Not enough operands for operator: {token}")
        else:
            raise RuntimeError(f"Unknown token in postfix: {token}")
    
    if len(stack) != 1:
        raise RuntimeError(f"Invalid postfix expression: {postfix_expr}")
    
    return stack[0]


def shuntingYard(formula:str):
    """Convert an infix formula to postfix notation using the Shunting Yard algorithm.
    This function takes a formula as input, replaces the operators with their single-character 
    representations,and then applies the Shunting Yard algorithm to convert it to postfix notation.

    Args:
        formula (str): The infix formula to convert, which may contain operators and operands.

    Returns:
        _type_: str: The postfix notation of the input formula, where operators follow their operands.
    """
    nominalManager.reset()
    inputFormula = replaceCharacters(formula)
    postfix = shuntingYardAlgorithm(inputFormula)
    reverted = replaceCharacters(postfix, True)
    return reverted
