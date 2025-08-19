import unittest
from ...one_step_frames.AST.parser.shunting_yard import shuntingYard
from ...one_step_frames.AST.core.abstract_syntax_tree import AbstractSyntaxTree
from ...one_step_frames.AST.errors.ast_error import ASTError


class TestShunt(unittest.TestCase):
    def test_shunting_yard(self):
        self.assertEqual(shuntingYard(""), "")

        tests = [
            ("#x<i(y)=>#x<#y", "x # y i < x # y # < =>"),
            ("i*(#x)<y=>#x<#y", "x # i* y < x # y # < =>"),
            ("#x<#i*(#x)", "x # x # i* # <"),
            ("w<#x=>w<#i*(#x)", "w x # < w x # i* # < =>"),
            ("@'w<x=>w<#i*(#x)", "w @' x < w x # i* # < =>"),
            ("w<#i*(#@'w)", "w w @' # i* # <"),
            ("i!i(y)", "y i i!"),                    # nested unary operators i! applied twice
            ("~#x&y", "x # ~ y &"),                   # unary ~ with binary &
            ("x=>y|z", "x y z | =>"),                  # implication and disjunction
            ("(x&y)|z", "x y & z |"),                 # parentheses to group
            ("i!(#@'x)", "x @' # i!"),              # unary i! with binary &
            ("i*(@z)", "z @ i*"),                    # unary i* with unary @
            ("i(#@'#@x)<z", "x @ # @' # i z <"),              # unary # with binary |
            ("i(i!(x))", "x i! i"),                   # nested i operators with parentheses
            ("i(i!(i*(x)))", "x i* i! i"),                   # nested i operators with parentheses
            ("w<#x=>w<#i!(#x)", "w x # < w x # i! # < =>"),
        ]

        for formula, expected_postfix in tests:
            # print(formula)
            reverted = shuntingYard(formula)
            self.assertEqual(reverted, expected_postfix)


class TestAbstractSyntaxTree(unittest.TestCase):
    def setUp(self):
        self.ast = AbstractSyntaxTree()

    def test_empty_formula(self):
        with self.assertRaises(ASTError):
            self.ast.buildTree("")

    def test_simple_operand(self):
        root = self.ast.buildTree("x")
        self.assertEqual(root.value, "x")
        self.assertEqual(root.arity, 0)
        self.assertIsNone(getattr(root, 'left', None))
        self.assertIsNone(getattr(root, 'right', None))
        self.assertIsNone(getattr(root, 'child', None))

    def test_unary_operator(self):
        root = self.ast.buildTree("#x")
        self.assertEqual(root.value, "#")
        self.assertEqual(root.arity, 1)
        self.assertIsNotNone(root.child)
        self.assertEqual(root.child.value, "x")
        self.assertEqual(root.child.arity, 0)

    def test_binary_operator(self):
        root = self.ast.buildTree("#x<#y")
        self.assertEqual(root.value, "<")
        self.assertEqual(root.arity, 2)
        self.assertIsNotNone(root.left)
        self.assertIsNotNone(root.right)
        self.assertEqual(root.left.value, "#")
        self.assertEqual(root.right.value, "#")
        self.assertEqual(root.left.child.value, "x")
        self.assertEqual(root.right.child.value, "y")

    def test_complex_formula(self):
        formula = "#x<y=>#x<#y"
        root = self.ast.buildTree(formula)
        # root should be =>
        self.assertEqual(root.value, "=>")
        self.assertEqual(root.arity, 2)
        # left subtree is (#x < y)
        left = root.left
        self.assertEqual(left.value, "<")
        self.assertEqual(left.arity, 2)
        self.assertEqual(left.left.value, "#")
        self.assertEqual(left.left.arity, 1)
        self.assertEqual(left.left.child.value, "x")
        self.assertEqual(left.right.value, "y")
        # right subtree is (#x < #y)
        right = root.right
        self.assertEqual(right.value, "<")
        self.assertEqual(right.arity, 2)
        self.assertEqual(right.left.value, "#")
        self.assertEqual(right.left.child.value, "x")
        self.assertEqual(right.right.value, "#")
        self.assertEqual(right.right.child.value, "y")

    def test_invalid_expression_not_enough_operands(self):
        with self.assertRaises(ASTError):
            self.ast.buildTree("#")

    def test_invalid_expression_extra_operands(self):
        with self.assertRaises(ASTError):
            self.ast.buildTree("x y")

    
    def test_clear_tree(self):

        formula = "#x<y=>#x<#y"
        self.ast.buildTree(formula)

        # Ensure the root is set before clearing
        self.assertIsNotNone(self.ast.getRoot())
        self.ast.clearTree()

        # After clearing, root should be None
        self.assertIsNone(self.ast.getRoot())
        self.assertEqual(self.ast.nodes, [])
        self.assertEqual(self.ast.variables, [])
        self.assertEqual(self.ast.constants, [])

    def test_clear_node(self):
        formula = "#x<y"
        root = self.ast.buildTree(formula)

        # Ensure tree is built properly
        self.assertEqual(root.value, "<")
        self.assertIsNotNone(root.left)
        self.assertIsNotNone(root.right)

        # Clear node manually
        self.ast.clearNode(root)

        # Root still exists, but its internals should be cleared
        self.assertIsNone(root.left)
        self.assertIsNone(root.right)
        self.assertIsNone(root.value)  # value is set to None in clearNode


if __name__ == "__main__":
    unittest.main()
