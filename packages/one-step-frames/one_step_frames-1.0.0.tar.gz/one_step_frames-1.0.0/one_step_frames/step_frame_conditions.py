from .util.core.preprocess import parseRule
from .util.core.formula import initFormula
from .util.core.solution_search import greedyFirstSearch
from .util.core.translate import translateCondition
from .util.core.simplify import simplifyConditon

def findStepFrameCondition(rule:str):
    rule = parseRule(rule)
    formula = initFormula(rule)
    result = greedyFirstSearch(formula)
    finalForm = result[0][-1]
    result = translateCondition(finalForm)
    result = simplifyConditon(result)
    return result
