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
            (r"(\x.x) (---2)", "-2.0"),
            ("if 0 then 2 else 1", "1.0"),
            ("if 1 then 2 else 2", "2.0"),
            ("if 0 then 2 else if 1 then 3 else 4", "3.0"),
            ("if 0 then 2 else if 0 then 3 else 4", "4.0"),
            ("if 0 == 0 then 5 else 6", "5.0"),
            ("if 0 <= 1 then 6 else 7", "6.0"),
            ("if 1 <= 0 then 6 else 7", "7.0"),
            ("let x = 1 in if x == 1 then 8 else 9", "8.0"),
            ("let x = 0 in if x == 1 then 8 else 9", "9.0"),
            ("let f = \\x.x in f 10", "10.0"),
            ("let f = \\x.x+1 in f 10", "11.0"),
            ("let f = \\x.x*6 in let g = \\x.x+1 in f (g 1)", "12.0"),
            ("let f = \\x.x*6 in let g = \\x.x+1 in g (f 2)", "13.0"),
            ("let f = \\x.x*6 in let f = \\x.x+1 in f (f 2) + 10", "14.0"),
            ("letrec f = \\n. if n==0 then 1 else n*f(n-1) in f 4", "24.0"),
            ("letrec f = \\n. if n==0 then 0 else 1 + 2*(n-1) + f(n-1) in f 6", "36.0")
        ]
        for input_expr, expected in tests:
            with self.subTest(input=input_expr):
                result = interpret(input_expr)
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()