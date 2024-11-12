import unittest
from interpreter import interpret

class TestInterpreter(unittest.TestCase):
    def test_lazy_evaluation(self):
        # Test that the interpreter follows lazy evaluation strategy
        tests = [
            (r"\x.(\y.y)x", r"(\x.((\y.y) x))"),
            (r"(\x.a x) ((\x.x)b)", r"(a ((\x.x) b))")
        ]
        for input_expr, expected in tests:
            with self.subTest(input=input_expr):
                result = interpret(input_expr)
                self.assertEqual(result, expected)

    def test_reductions(self):
        # Test various reduction cases
        tests = [
            (r"(\x.x) (1--2)", "3.0"),
            (r"(\x.x) (1---2)", "-1.0"),
            (r"(\x.x + 1) 5", "6.0"),
            (r"(\x.x * x) 3", "9.0"),
            (r"(\x.\y.x + y) 3 4", "7.0"),
            ("1-2*3-4", "-9.0"),
            (r"(\x.x * x) 2 * 3", "12.0"),
            (r"(\x.x * x) (-2) * (-3)", "-12.0"),
            (r"((\x.x * x) (-2)) * (-3)", "-12.0"),
            (r"(\x.x) (---2)", "-2.0")
        ]
        for input_expr, expected in tests:
            with self.subTest(input=input_expr):
                result = interpret(input_expr)
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()