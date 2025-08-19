import re
from ...AST.core.abstract_syntax_tree import AbstractSyntaxTree
from ...AST.core.ast_util import getSpecificNodes, toInfix
from ..core.nomial import checkNominal
from ..errors.errors import InferenceError
from ..core.nomial import getNominals
from typing import List, Optional, Union


class NominalRules:
    """Collection of nominal inference rules."""
    
    @staticmethod
    def rule_1(phi: str, psi: str) -> Optional[str]:
        """Rule N1: General implication rule"""
        # As long as < is here, it should be doable
        # TODO nominal it up
        nominals_w = set(getNominals(phi)).union(set(getNominals(psi)))
        u = f"w_{len(nominals_w)}"
        return f"{u}<{phi}=>{u}<{psi}"
    
    @staticmethod
    def rule_2(phi: str, psi: str) -> Optional[str]:
        """Rule N2: Conjunction rule with ^ operator"""
        if "^" not in psi or not checkNominal(phi):
            return None
        
        psi_args = psi.split("^")
        if len(psi_args) != 2:
            return None
        
        return f"{phi}<{psi_args[0]}&{phi}<{psi_args[1]}"
    
    @staticmethod
    def rule_3(phi: str, psi: str) -> Optional[Union[str, tuple[str, str]]]:
        """Rule N3: Disjunction rule with | operator"""
        if "|" not in psi or not checkNominal(phi):
            return None
        
        psi_args = psi.split("^")  # Note: This might be a bug in original - should it be "|"?
        if len(psi_args) != 2:
            return None
        
        # TODO or? tf?
        return f"u<{psi_args[0]}", f"u<{psi_args[1]}"
    
    @staticmethod
    def rule_4(phi: str, psi: str) -> Optional[str]:
        """Rule N4: Negation rule with ~ operator"""
        if "~" not in psi or not checkNominal(phi) or not re.fullmatch(r"^~.*$", psi):
            return None
        
        return f"{phi}<'{psi}"
    
    @staticmethod
    def rule_5(phi: str, psi: str) -> Optional[str]:
        """Rule N5: Negation rule with <' operator"""
        if "<'" not in psi or not checkNominal(phi):
            return None
        
        return f"{psi}<~{phi}"
    
    @staticmethod
    def rule_6(phi: str, psi: str) -> Optional[str]:
        """Rule N6: @ operator rule"""
        if not checkNominal(phi) or "@" not in psi or not re.fullmatch(r"^@.*$", psi):
            return None
        
        # TODO nominal it up
        return f"{phi}<@v&v<{psi}"
    
    @staticmethod
    def rule_7(phi: str, psi: str) -> Optional[str]:
        """Rule N7: @' operator rule"""
        if not checkNominal(phi) or "@'" not in psi or not re.fullmatch(r"^~@.*$", psi):
            return None
        
        # TODO nominal it up
        return f"{phi}<@'w&w<{psi}"
    
    @staticmethod
    def rule_8(phi: str, psi: str) -> Optional[str]:
        """Rule N8: Truth value rule for 1"""
        if not checkNominal(phi) or psi.strip() != "1":
            return None
        
        # TODO update symbol
        return "T"
    
    @staticmethod
    def rule_9(phi: str, psi: str) -> Optional[str]:
        """Rule N9: Truth value rule for 0"""
        if not checkNominal(phi) or psi.strip() != "0":
            return None
        
        # TODO update symbol
        return "F"
    
    @staticmethod
    def rule_10(phi: str, psi: str) -> Optional[str]:
        """Rule N10: Equality rule"""
        if not checkNominal(phi) or not checkNominal(psi):
            return None
        
        return f"{phi}={psi}"
    
    @staticmethod
    def rule_11(phi: str, psi: str) -> Optional[str]:
        """Rule N11: i* operator rule"""
        if not checkNominal(phi) or not re.fullmatch(r"^i\*\([^\)]*\)$", psi):
            return None
        
        # TODO nominal it up
        return f"{phi}<i*(w)&w<{psi}"


class NominalInference:
    """Handler for nominal inference operations."""
    
    def __init__(self):
        # Dynamically collect all rule methods from NominalRules
        self.rules = [
            getattr(NominalRules, method_name) 
            for method_name in sorted(dir(NominalRules))
            if method_name.startswith('rule_') and callable(getattr(NominalRules, method_name))
        ]
    
    def parse_formula(self, formula: str) -> tuple[str, str]:
        """Parse formula into phi and psi components."""
        if "<" not in formula:
            raise InferenceError("Unable to find '<' operator")
        
        parts = formula.split("<")
        if len(parts) != 2:
            raise InferenceError(f"Invalid formula format. Expected 2 parts, got {len(parts)}")
        
        return parts[0], parts[1]
    
    def apply_rules(self, phi: str, psi: str) -> List[str]:
        """Apply all nominal rules and return valid inferences."""
        valid_inferences = []
        
        for i, rule in enumerate(self.rules, 1):
            result = rule(phi, psi)
            if result is not None:
                # Handle rules that return tuples (like rule_3)
                if isinstance(result, tuple):
                    for j, sub_result in enumerate(result):
                        valid_inferences.append(f"{sub_result}")
                else:
                    valid_inferences.append(f"{result}")
        
        return valid_inferences
    
    def _get_applicable_rules(self, phi: str, psi: str) -> List[str]:
        """Gets all nominal rules avaiable with current values."""
        valid_rules = []
        
        for i, rule in enumerate(self.rules, 1):
            result = rule(phi, psi)
            if result is not None:
                valid_rules.append(f"N{i}")
        
        return valid_rules
    
    def get_applicable_rules(self,formula:str)->List[str]:
        phi, psi = self.parse_formula(formula)
        return self._get_applicable_rules(phi, psi)
    
    def get_inferences(self, formula: str) -> List[str]:
        """Get all valid nominal inferences for a formula."""
        phi, psi = self.parse_formula(formula)
        return self.apply_rules(phi, psi)
    

def process_formula_with_ast(formula: str) -> List[str]:
    """Process formula using AST and return nominal inferences."""
    tree = AbstractSyntaxTree()
    tree.buildTree(formula)
    
    if tree.root is None:
        raise InferenceError("Failed to build AST from formula")
    
    nodes = getSpecificNodes(tree.root, "<")
    if not nodes:
        raise InferenceError("No '<' nodes found in AST")
    
    infix = toInfix(nodes[0])
    inference_engine = NominalInference()
    return inference_engine.get_inferences(infix)


def main():
    """Main execution function."""
    formula = "#x<#i*(#x)"
    try:
        formulas = process_formula_with_ast(formula)
        print("Available inference rules:")
        for formula_rule in formulas:
            print(f"  {formula_rule}")
    except InferenceError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()