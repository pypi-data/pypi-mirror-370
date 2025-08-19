from ...AST.core.abstract_syntax_tree import AbstractSyntaxTree
from ...AST.core.ast_util import getSpecificNodes,toInfix
from ..errors.errors import InferenceError
from .nominal_rules import NominalInference
from .adjunction_rules import AdjunctionInference


def processFormulaWithAST(formula: str) -> list[str]:
    """Process a formula using an Abstract Syntax Tree (AST) to extract specific nodes.
    This function builds an AST from the given formula and retrieves all nodes that match
    the specified condition (in this case, nodes with the '<' operator).

    Args:
        formula (str): The formula to process, which should be a valid string representation

    Raises:
        InferenceError: If the AST cannot be built from the formula or if no nodes with the '<' operator are found.
        InferenceError: If no '<' nodes are found in the AST.

    Returns:
        list[str]: A list of strings representing the infix notation of the subtrees/nodes that 
        match the condition.
        Each string corresponds to a node/subtree in the AST that contains the '<' operator.
    """
    tree = AbstractSyntaxTree()
    tree.buildTree(formula)
    
    if tree.root is None:
        raise InferenceError("Failed to build AST from formula")
    
    nodes = getSpecificNodes(tree.root, "<")
    if not nodes:
        raise InferenceError("No '<' nodes found in AST")
    
    infixStrings = [toInfix(i) for i in nodes]

    return infixStrings


def inferenceRules(formula:str)->dict[str,list[str]]:
    """Get all inference rules for a given formula.
    It runs the nominal and adjunction inference engines
    and returns a dictionary with the subformulae(formula/statements with <) as keys 
    and lists of applicable inference rules as values
    Args:
        formula (str): The formula to process.
    Returns:
        dict[str, list[str]]: A dictionary where keys are formulae and values are lists
        of inference rules applicable to those formulae.
    """
    formulae = processFormulaWithAST(formula)
    inferenceEngignes = [NominalInference(),AdjunctionInference()]
    resultDict = {i:[] for i in formulae}
    trackRules = []

    for engine in inferenceEngignes:
        for form in resultDict.keys():
            availableInferenceRules = engine.get_inferences(form)
            availableRules = engine.get_applicable_rules(form)
            trackRules.extend(availableRules)
            resultDict[form].extend(availableInferenceRules)
    
    return resultDict


if __name__=="__main__":
    formula = "#x<i(y)=>#x<#y"
    inferenceRules(formula)