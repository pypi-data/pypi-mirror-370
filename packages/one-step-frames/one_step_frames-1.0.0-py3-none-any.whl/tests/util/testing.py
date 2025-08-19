import unittest
from ...one_step_frames.util.core.preprocess import checkIfNoTextAfterCharacter, checkIfNoTextBeforeCharacter, checkIfValidCharacters
from ...one_step_frames.util.errors.errors import InputError
from ...one_step_frames.util.core import formula as formula_util


class TestPreprocess(unittest.TestCase):
    def test_checkIfNoTextAfterCharacter(self):
        self.assertTrue(checkIfNoTextAfterCharacter("test#", "#"))
        self.assertFalse(checkIfNoTextAfterCharacter("test#text", "#"))
        self.assertTrue(checkIfNoTextAfterCharacter("test", "#"))

    def test_checkIfNoTextBeforeCharacter(self):
        self.assertTrue(checkIfNoTextBeforeCharacter("#test", "#"))
        self.assertFalse(checkIfNoTextBeforeCharacter("text#test", "#"))
        self.assertTrue(checkIfNoTextBeforeCharacter("test", "#"))

    def test_checkIfValidCharacters(self):
        valid_rule = "a#b@c->d<->e"
        invalid_rule = "a#b@c->d<->e$"

        self.assertTrue(checkIfValidCharacters(valid_rule))
        with self.assertRaises(InputError):
            checkIfValidCharacters(invalid_rule)


class TestFormula(unittest.TestCase):
    def test_checkIfFree(self):
        self.assertTrue(formula_util.checkIfFree("x"))
        self.assertFalse(formula_util.checkIfFree("#x"))
        self.assertFalse(formula_util.checkIfFree("@x"))
        self.assertFalse(formula_util.checkIfFree("#@'@x"))
    
    def test_initAtomicFormula(self):
        self.assertEqual(formula_util.initAtomicFormula("x"), "i(x)")
        self.assertEqual(formula_util.initAtomicFormula("y"), "i(y)")
        self.assertEqual(formula_util.initAtomicFormula("#x"), "#x")
        self.assertEqual(formula_util.initAtomicFormula("@x"), "@x")

    def test_initFrmula(self):
        self.assertEqual(formula_util.initFormula("x"), "i(x)")
        self.assertEqual(formula_util.initFormula("#x"), "#x")
        self.assertEqual(formula_util.initFormula("@x"), "@x")
        self.assertEqual(formula_util.initFormula("x&y"), "i(x)&i(y)")
        self.assertEqual(formula_util.initFormula("x=>y"), "i(x)=>i(y)")

    def test_findAtomicFormulas(self):
        formula = "x&y|z"
        expected = ["x", "y", "z"]
        result = formula_util.findAtomicFormulas(formula)
        self.assertEqual(result, expected)
    
    def test_getConnectives(self):
        self.assertEqual(formula_util.getConnectives("x&y|z"), ["&", "|"])
        self.assertEqual(formula_util.getConnectives("x=>y"), ["=>"])
        self.assertEqual(formula_util.getConnectives("x<->y"), ["<->"])
        self.assertEqual(formula_util.getConnectives("x#y@z"), ["#", "@"])
        self.assertEqual(formula_util.getConnectives(""),[])
    
    def test_getVariable(self):
        self.assertEqual(formula_util.getVariable("x&y|z"), ["x", "y", "z"])
        self.assertEqual(formula_util.getVariable("#x@z"), ["x", "z"])
        self.assertEqual(formula_util.getVariable("i(x)"), ["x"])
        self.assertEqual(formula_util.getVariable("i(x)&i(y)"), ["x", "y"])
        self.assertEqual(formula_util.getVariable(""), [])
        self.assertEqual(formula_util.getVariable("i"), [])
        self.assertEqual(formula_util.getVariable("#"), [])
        self.assertEqual(formula_util.getVariable("@'=>@"), [])


if __name__ == "__main__":
    unittest.main()