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
            ("(if 1 == 1 then \\x.x+1 else \\x.x+2) 5 + 10", "16.0"),
            ("if 1 == 1 then 1 else 2 + 1", "1.0"),
            ("1 ;; 2", "1.0 ;; 2.0"),
            ("1 ;; 2 ;; 3", "1.0 ;; 2.0 ;; 3.0"),
            ("1+1 ;; (\\x.x)a ;; (\\x.x+x)2", "2.0 ;; a ;; 4.0"),
            ("1:2 ;; 1:2:#", "(1.0 : 2.0) ;; (1.0 : (2.0 : #))"),
            ("(1)", "1.0"),
            ("#", "#"),
            ("1:2:3:#", "(1.0 : (2.0 : (3.0 : #)))"),
            ("(\\x.x) #", "#"),
            ("(\\x.\\y.x) 1:# a", "(1.0 : #)"),
            ("(\\x.\\y.y) a 1:#", "(1.0 : #)"),
            ("let f = \\x.x+1 in (f 1) : (f 2) : (f 3) : #", "(2.0 : (3.0 : (4.0 : #)))"),
            ("1:2 == 1:2", "1.0"),
            ("1:2 == 1:3", "0.0"),
            ("1:2:# == 1:2:#", "1.0"),
            ("(1-2) : (2+2) : # == (-1):4:#", "1.0"),
            ("hd a", "(hd a)"),
            ("hd (1:2:#)", "1.0"),
            ("hd 1:2:#", "1.0"),
            ("tl a", "(tl a)"),
            ("tl (1:2:#)", "(2.0 : #)"),
            ("tl 1:2:#", "(2.0 : #)"),
            ("letrec map = \\f. \\xs. if xs==# then # else (f (hd xs)) : (map f (tl xs)) in (map (\\x.x+1) (1:2:3:#))", "(2.0 : (3.0 : (4.0 : #)))")
        ]
        for input_expr, expected in tests:
            with self.subTest(input=input_expr):
                result = interpret(input_expr)
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()