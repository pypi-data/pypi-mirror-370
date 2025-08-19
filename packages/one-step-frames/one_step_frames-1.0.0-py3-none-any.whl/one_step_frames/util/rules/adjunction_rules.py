import re
from ..errors.errors import InferenceError
from ...AST.core.abstract_syntax_tree import AbstractSyntaxTree
from ...AST.core.ast_util import getSpecificNodes, toInfix
from typing import List, Optional, Callable


class AdjunctionRules:
    """Collection of adjunction inference rules."""
    
    @staticmethod
    def rule_1(phi: str, psi: str) -> Optional[str]:
        """Rule A1: If psi matches #.*, return @'{phi}<{psi}"""
        if re.fullmatch(r"^#.*$", psi):
            return f"@'{phi}<{psi.replace("#","",1)}"
        return None
    
    @staticmethod
    def rule_2(phi: str, psi: str) -> Optional[str]:
        """Rule A2: If psi matches #'.*, return @{phi}<{psi}"""
        if re.fullmatch(r"^#'.*$", psi):
            return f"@{phi}<{psi}"
        return None
    
    @staticmethod
    def rule_3(phi: str, psi: str) -> Optional[str]:
        """Rule A3: If psi matches i(...), return i*({phi})<{content_inside_i}"""
        match = re.fullmatch(r"^i\(([^\)]*)\)$", psi)
        if match:
            content_inside_i = match.group(1)
            return f"i*({phi})<{content_inside_i}"
        return None
    
    @staticmethod
    def rule_4(phi: str, psi: str) -> Optional[str]:
        """Rule A4: If psi matches i!(...), return i({phi})<{content_inside_i}"""
        match = re.fullmatch(r"^i!\(([^\)]*)\)$", psi)
        if match:
            content_inside_i = match.group(1)
            return f"i({phi})<{content_inside_i}"
        return None



class AdjunctionInference:
    """Handler for adjunction inference operations."""
    
    def __init__(self):
        # Dynamically collect all rule methods from AdjunctionRules
        self.rules = [
            getattr(AdjunctionRules, method_name) 
            for method_name in sorted(dir(AdjunctionRules))
            if method_name.startswith('rule_') and callable(getattr(AdjunctionRules, method_name))
        ]
    
    def parse_formula(self, formula: str) -> tuple[str, str]:
        """Parse formula into phi and psi components."""
        if "<" not in formula:
            raise InferenceError("Unable to find '<' operator")
        
        parts = formula.split("<")
        if len(parts) != 2:
            raise InferenceError(f"Invalid formula format. Expected 2 parts, got {len(parts)}")
        
        return parts[0], parts[1]
    
    def _get_applicable_rules(self, phi: str, psi: str) -> List[str]:
        """Gets all adjunction rules avaiable with current values."""
        valid_rules = []
        
        for i, rule in enumerate(self.rules, 1):
            result = rule(phi, psi)
            if result is not None:
                valid_rules.append(f"A{i}")
        
        return valid_rules
    

    def apply_rules(self, phi: str, psi: str) -> List[str]:
        """Apply all adjunction rules and return valid inferences."""
        valid_inferences = []
        
        for i, rule in enumerate(self.rules, 1):
            result = rule(phi, psi)
            if result is not None:
                valid_inferences.append(f"{result}")
        
        return valid_inferences
    
    def get_applicable_rules(self,formula:str)->List[str]:
        phi, psi = self.parse_formula(formula)
        return self._get_applicable_rules(phi, psi)
    
    def get_inferences(self, formula: str) -> List[str]:
        """Get all valid adjunction inferences for a formula."""
        phi, psi = self.parse_formula(formula)
        return self.apply_rules(phi, psi)


def process_formula_with_ast(formula: str) -> List[str]:
    """Process formula using AST and return adjunction inferences."""
    tree = AbstractSyntaxTree()
    tree.buildTree(formula)
    
    if tree.root is None:
        raise InferenceError("Failed to build AST from formula")
    
    nodes = getSpecificNodes(tree.root, "<")
    if not nodes:
        raise InferenceError("No '<' nodes found in AST")
    
    infix = toInfix(nodes[0])
    inference_engine = AdjunctionInference()
    return inference_engine.get_inferences(infix)


def main():
    """Main execution function."""
    formula = "#x<i(y)"
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