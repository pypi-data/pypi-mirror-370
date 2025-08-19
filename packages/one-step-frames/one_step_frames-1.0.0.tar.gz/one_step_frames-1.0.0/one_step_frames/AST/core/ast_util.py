from ..core.abstract_syntax_tree import Node


def getLeafNodes(node:Node,parent=None,result=None):
    """Get all leaf nodes in the AST.
    This function traverses the AST and collects all leaf nodes (nodes without children).
    A leaf node is defined as a node that has no children, meaning it does not have
    left or right children in the case of binary operators, or a child in the case of
    unary operators. The function also collects the parent of each leaf node.

    Args:
        node (Node): The current node in the AST to check for leaf nodes.
        parent (_type_, optional): Parent of node. Defaults to None.
        result (_type_, optional): list used to track leaf nodes. Defaults to None.

    Returns:
        list(tuple(Node,Node)): A list of tuples, where each tuple contains a leaf node and its parent.
        Each tuple is of the form (leaf_node, parent_node).
    """
    if result is None:
        result = []

    if node is None:
        return result
    
    if node.arity==2:
        if (node.left!=None):
            getLeafNodes(node.left,node,result)
        if (node.right!=None):
            getLeafNodes(node.right,node,result)
    else:
        if node.child!=None:
            getLeafNodes(node.child,node,result)
        else:
            result.append((node,parent))

    return result


def getSpecificNodes(node:Node,searchValue:str="",result=None,):
    """Get all nodes in the AST that match a specific value.
    This function traverses the AST and collects all nodes that have a value matching
    the specified search value. It can be used to find specific operators or variables
    within the AST. The search is case-sensitive and matches the value exactly.

    Args:
        node (Node): The current node in the AST to check for matching values.
        searchValue (str, optional): Value to search for. Defaults to "".
        result (_type_, optional): list tracking current searched for nodes. Defaults to None.

    Returns:
        list(tuple): A list of nodes that match the search value.
        Each node in the list is an instance of Node that has the specified value.
    """
    if result is None:
        result = []

    if node is None:
        return result
    
    if (node.value==searchValue):
        result.append(node)

    if node.arity==2:
        if (node.left!=None):
            getSpecificNodes(node.left,searchValue,result)
        if (node.right!=None):
            getSpecificNodes(node.right,searchValue,result)

    else:
        if node.child!=None:
            getSpecificNodes(node.child,searchValue,result)

    return result


def toInfix(node:Node) -> str:
    """Convert an AST node to its infix string representation.
    This function recursively converts an AST node to its infix notation.
    It handles nodes with different arities (0, 1, or 2) and formats the output accordingly.
    - For nodes with arity 0, it returns the value as a string.
    - For nodes with arity 1, it formats the child expression with the operator.
    - For nodes with arity 2, it formats the left and right child expressions
      with the operator in between.

    Args:
        node (Node): The AST node to convert to infix notation.

    Raises:
        ValueError: If the node has an unsupported arity (not 0, 1, or 2).

    Returns:
        str: The infix string representation of the node.
    """
    if node is None:
        return ""

    if node.arity == 0:
        return str(node.value)
    elif node.arity == 1:
        if node.child is None:
            return ""
        child_expr = toInfix(node.child) 
        # Only add parentheses for i, i*, and i! operators
        if node.value in ["i", "i*", "i!"]:
            return f"{node.value}({child_expr})"
        else:
            return f"{node.value}{child_expr}"

    elif node.arity == 2:
        if node.left is None:
            return ""
        left_expr = toInfix(node.left)

        if node.right is None:
            return ""
        right_expr = toInfix(node.right)
        
        return f"{left_expr}{node.value}{right_expr}"

    else:
        raise ValueError(f"Unsupported arity: {node.arity}")