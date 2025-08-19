from ..parser.shunting_yard import shuntingYard
from .abstract_operator import AbstractOperator
from ..errors.ast_error import ASTError

# Default operators for the Abstract Syntax Tree
defaultOperators = operators = [
    # perf 2
    AbstractOperator("=>",2,2),

    # perf 1
    AbstractOperator("<",2,1),
    AbstractOperator("<'",2,1),

    #perf 0
    AbstractOperator("#",1),
    AbstractOperator("#'",1),
    AbstractOperator("@",1),
    AbstractOperator("@'",1),
    AbstractOperator("~",1),
    AbstractOperator("i*",1),
    AbstractOperator("i!",1),
    AbstractOperator("i",1),

    AbstractOperator("^",2),
    AbstractOperator("&",2),
    AbstractOperator("->",2),
    AbstractOperator("<->",2),
]


class Node:
    def __init__(self, arity, value) -> None:
        self.arity = arity 
        self.value = value
        # Initialize children based on arity
        if (arity == 2):
            # Binary operator - has left and right children
            self.left = None
            self.right = None
        else:
            # Unary operator or operand - has one child
            self.child = None
    
    def setLeft(self, leftNode):
        self.left = leftNode
    
    def setRight(self, rightNode):
        self.right = rightNode
    
    def setChild(self, childNode):
        self.child = childNode
    
    def __str__(self) -> str:
        return f"Node(arity:{self.arity}, value:{self.value})"


class AbstractSyntaxTree:
    """Represents an Abstract Syntax Tree (AST) for modal logic formulas.
    This class provides methods to build the tree from a formula string,
    clear the tree, print the tree structure, and find operators."""
    def __init__(self, operators: list[AbstractOperator]=defaultOperators) -> None:
        self.root = None
        self.nodes = []
        self.operators = operators
        self.operatorsMap = {op.getSymbol(): op for op in operators}
        self.operatorsArityMap = {op.getSymbol(): op.getArity() for op in operators}
        self.variables = []
        self.constants = []
    
    def getRoot(self):
        return self.root
    
    def findOperator(self, symbol: str) -> AbstractOperator | None:
        for op in self.operators:
            if op.getSymbol() == symbol:
                return op
        return None
    

    def buildTree(self, formula: str):
        """Builds an Abstract Syntax Tree from a given formula string.
        This method uses the shunting yard algorithm to convert the formula
        into postfix notation, then constructs the tree using a stack-based approach.

        Args:
            formula (str): The formula string to build the tree from.

        Raises:
            ASTError: If the formula is empty or if there are not enough operands for an operator.
            ASTError: If the postfix notation is invalid or if there are too many operands left in the stack after processing.
            ASTError: If an unsupported operator arity is encountered.
            ASTError: If there are not enough operands for a unary or binary operator.
            ASTError: If the postfix notation is empty after processing.

        Returns:
            Node: The root node of the constructed Abstract Syntax Tree.
        """
        postfixNotation = shuntingYard(formula).split()

        if not postfixNotation:
            raise ASTError("Cannot build tree from empty postfix notation")
        
        # Use a stack-based approach to build the tree from postfix notation
        stack = []
        
        for token in postfixNotation:
            operator = self.findOperator(token)
            
            if operator is not None:
                # It's an operator
                arity = operator.getArity()
                node = Node(arity, token)
                
                if arity == 1:
                    # Unary operator - needs 1 operand
                    if len(stack) < 1:
                        raise ASTError(f"Not enough operands for unary operator {token}")
                    node.child = stack.pop()
                elif arity == 2:
                    # Binary operator - needs 2 operands
                    if len(stack) < 2:
                        raise ASTError(f"Not enough operands for binary operator {token}")
                    # Note: In postfix, the right operand is popped first
                    node.right = stack.pop()
                    node.left = stack.pop()
                else:
                    raise ASTError(f"Unsupported arity {arity} for operator {token}")
                
                stack.append(node)
            else:
                # It's an operand (variable or constant)
                node = Node(0, token)  # Operands have arity 0
                stack.append(node)
        
        if len(stack) != 1:
            raise ASTError(f"Invalid expression: stack has {len(stack)} elements after processing")
        
        self.root = stack[0]
        return self.root
    

    def clearNode(self,node: Node):
        """Recursively clear a node and its children to help with deallocation.
        This method sets the children of the node to None and clears the value.
        It is useful for deallocating memory when the tree is no longer needed.

        Args:
            node (Node): The node to clear.
        """
        if node is None:
            return
        if node.arity == 1:
            if (node.child!=None):
                self.clearNode(node.child)
                node.child = None
        elif node.arity == 2:
            if (node.left!=None):
                self.clearNode(node.left)
                node.left = None
            if (node.right!=None):
                self.clearNode(node.right)
                node.right = None
        # Remove reference to value as well (optional)
        node.value = None


    def clearTree(self):
        """Clear the entire tree by deallocating nodes and resetting the root.
        This method recursively clears all nodes in the tree and resets the root to None.
        It also clears any lists tracking nodes, variables, and constants."""
        if (self.root!=None):
            self.clearNode(self.root)

        self.root = None
        self.nodes.clear()  # if you are tracking nodes in self.nodes list
        self.variables.clear()
        self.constants.clear()


    def printTree(self):
        """Print the Abstract Syntax Tree in a structured format.
        This method prints the tree structure starting from the root node.
        It uses a helper method to recursively print each node with its value and arity.
        If the tree is empty, it prints a message indicating that the tree is empty.
        The output is formatted to visually represent the tree structure with connectors.
        """
        if self.root is None:
            print("Empty tree")
            return
        
        print("Abstract Syntax Tree:")
        print("=" * 30)
        self._printNode(self.root, "", True)
        print("=" * 30)
    

    def _printNode(self, node: Node, prefix: str, isLast: bool):
        """Helper method to recursively print nodes with tree structure"""
        if node is None:
            return
        
        # Print current node
        connector = "└── " if isLast else "├── "
        print(f"{prefix}{connector}'{node.value}' (arity: {node.arity})")
        
        # Prepare prefix for children
        extension = "    " if isLast else "│   "
        new_prefix = prefix + extension
        
        # Print children based on arity
        if node.arity == 1:
            # Unary operator - has one child
            if hasattr(node, 'child') and node.child is not None:
                self._printNode(node.child, new_prefix, True)
        elif node.arity == 2:
            # Binary operator - has left and right children
            if hasattr(node, 'left') and hasattr(node, 'right'):
                # Print left child first (not last if right exists)
                has_right = node.right is not None
                if node.left is not None:
                    self._printNode(node.left, new_prefix, not has_right)
                
                # Print right child (always last)
                if node.right is not None:
                    self._printNode(node.right, new_prefix, True)
    

    def printTreeCompact(self):
        """Print a more compact representation of the tree"""
        if self.root is None:
            print("Empty tree")
            return
        
        print("Compact Tree Representation:")
        print(self._nodeToString(self.root))
    

    def _nodeToString(self, node: Node) -> str:
        """Convert a node and its children to a string representation"""
        if node is None:
            return "None"
        
        if node.arity == 0:
            # Leaf node (variable/constant)
            return str(node.value)
        elif node.arity == 1:
            # Unary operator
            if hasattr(node, 'child') and node.child is not None:
                return f"{node.value}({self._nodeToString(node.child)})"
            else:
                return f"{node.value}(?)"
        elif node.arity == 2:
            # Binary operator
            left_str = "?" if not hasattr(node, 'left') or node.left is None else self._nodeToString(node.left)
            right_str = "?" if not hasattr(node, 'right') or node.right is None else self._nodeToString(node.right)
            return f"({left_str} {node.value} {right_str})"
        else:
            return str(node.value)
