from .priority_stack import PriorityStack
from ..rules.inference_rules import inferenceRules
from ..rules.ackermann_rules import findVariables,applyAckermannRule,ackermannHeuristic


def greedyFirstSearch(formula: str) -> tuple[list[str], list[str]]:
    """Perform a greedy first search on the formula to find a solution.
    A Priority stack is used with the ackermann heuristic 
    to prioritize items.

    Args:
        formula (str): The formula to search on.
        
    Returns:
        list[list[str]]: A list, index 0 is states, and index 1 is the log of the search.
    """
    variables = findVariables(formula)
    numberVariables = len(variables) 
    stillSearch = True
    iterations = 0

    trackState = []
    trackLog = []

    pq = PriorityStack()
    pq.push(0,formula)   

    while not pq.empty() and stillSearch and iterations<30:
        iterations+=1
        item = pq.pop()
        trackState.append(item)
        trackLog.append(f"Current formula:{item}")

        if (item==None):
            break

        currentVariables = findVariables(item)
        appliedAck = False

        # Goal test
        if len(currentVariables)==0:
            stillSearch = False
            trackLog.append(f"Goal found:{item}")
            continue
        
        #Check ackermann rule
        for var in variables:
            newForm = applyAckermannRule(item)

            if (newForm!= item):
                trackLog.append(f"Applying Ackermann rule to {item}, yielding {newForm}")
                pq.push(5,newForm)
                appliedAck = True
                break
        
        if appliedAck:
            continue
        
        # Do inference rules now
        currentInferenceRules = inferenceRules(item)

        for subform in currentInferenceRules.keys():
            for replacement in currentInferenceRules[subform]:
                tempFormula = item
                tempFormula = tempFormula.replace(subform,replacement)

                if (tempFormula.count("=>"))>1:
                    continue

                score = ackermannHeuristic(tempFormula,numberVariables)
                # print(f"ADDED {tempFormula} with prio {score}")
                trackLog.append(f"Added potential formula {tempFormula} with priority {score}")
                pq.push(score,tempFormula)

    return trackState,trackLog

