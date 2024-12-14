import sys
import lark
from lark import Lark, Transformer, Tree


print(f"Python version: {sys.version}")
print(f"Lark version: {lark.__version__}")

#  run/execute/interpret source code
def interpret(source_code):
    print("SOURCE: ")
    print(source_code)
    print()
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    print("AST:", ast)
    result_ast = evaluate(ast)
    print("EVALUATED:", result_ast)
    result = linearize(result_ast)
    print("LINEARIZED:", result)
    return result

# convert concrete syntax to CST
parser = Lark(open("grammar.lark").read(), parser='lalr')

# convert CST to AST
class LambdaCalculusTransformer(Transformer):
    def plus(self, args):
        return ('plus', args[0], args[1])
    
    def minus(self, args):
        return ('minus', args[0], args[1])
    
    def multiply(self, args):
        return ('multiply', args[0], args[1])
    
    def lam(self, args):
        name, body = args
        return ('lam', str(name), body)

    def app(self, args):
        new_args = [(arg.data, arg.children[0]) if isinstance(arg, Tree) and arg.data == 'int' else arg for arg in args]
        return ('app', *new_args)

    def var(self, args):
        token, = args
        return ('var', str(token))

    def NAME(self, token):
        return str(token)
    
    def number(self, args):
        token, = args
        return float(token)  # Return the number directly as a float

    def negation(self, args):
        value, = args
        if isinstance(value, (int, float)):
            return -value
        return ('negation', value)
    
    def let(self, args):
        name, value, body = args
        return ('let', str(name), value, body)

    def rec(self, args):
        name, value, body = args
        return ('rec', str(name), value, body)

    def fix(self, args):
        expr, = args
        return ('fix', expr)

    def if_then_else(self, args):
        condition, then_expr, else_expr = args
        return ('if', condition, then_expr, else_expr)

    def eq(self, args):
        left, right = args
        return ('eq', left, right)

    def lt(self, args):
        left, right = args
        return ('lt', left, right)

    def gt(self, args):
        left, right = args
        return ('gt', left, right)

    def ge(self, args):
        left, right = args
        return ('ge', left, right)

    def le(self, args):
        left, right = args
        return ('le', left, right)

    def seq(self, args):
        return ('seq', args[0], args[1])

    def hd(self, args):
        return ('hd', args[0])

    def tl(self, args):
        return ('tl', args[0])

    def nil(self, args):
        return ('nil',)

    def cons(self, args):
        return ('cons', args[0], args[1])

def linearize(ast):
    print("LINEARIZING:", ast)
    if isinstance(ast, (float, int)):
        return f"{ast:.1f}"
    
    if isinstance(ast, tuple):
        if ast[0] == 'hd':
            # Don't evaluate again, just format what we have
            if isinstance(ast[1], tuple) and ast[1][0] == 'var':
                return f"(hd {ast[1][1]})"  # Format unevaluated hd of variable
            elif isinstance(ast[1], tuple) and ast[1][0] == 'cons':
                return linearize(evaluate(ast))  # Evaluate and linearize the result
            return f"(hd {linearize(ast[1])})"  # Format other unevaluated hd expressions
        
        elif ast[0] == 'cons':
            return f"({linearize(ast[1])} : {linearize(ast[2])})"
        
        elif ast[0] == 'var':
            return ast[1]
        
        elif ast[0] == 'lam':
            return f"(\\{ast[1]}.{linearize(ast[2])})"
        
        elif ast[0] == 'app':
            return f"({linearize(ast[1])} {linearize(ast[2])})"
        
        elif ast[0] == 'plus':
            return f"({linearize(ast[1])} + {linearize(ast[2])})"
        
        elif ast[0] == 'minus':
            return f"({linearize(ast[1])} - {linearize(ast[2])})"
        
        elif ast[0] == 'multiply':
            return f"({linearize(ast[1])} * {linearize(ast[2])})"
        
        elif ast[0] == 'negation':
            return f"(-{linearize(ast[1])})"
        
        elif ast[0] == 'number':
            return f"{ast[1]:.1f}"
        
        elif ast[0] == 'let':
            return f"(let {ast[1]} = {linearize(ast[2])} in {linearize(ast[3])})"
        
        elif ast[0] == 'rec':
            return f"(letrec {ast[1]} = {linearize(ast[2])} in {linearize(ast[3])})"
        
        elif ast[0] == 'fix':
            return f"(fix {linearize(ast[1])})"
        
        elif ast[0] == 'if':
            return f"(if {linearize(ast[1])} then {linearize(ast[2])} else {linearize(ast[3])})"
        
        elif ast[0] == 'eq':
            return f"({linearize(ast[1])} == {linearize(ast[2])})"
        
        elif ast[0] == 'lt':
            return f"({linearize(ast[1])} < {linearize(ast[2])})"
        
        elif ast[0] == 'gt':
            return f"({linearize(ast[1])} > {linearize(ast[2])})"
        
        elif ast[0] == 'ge':
            return f"({linearize(ast[1])} >= {linearize(ast[2])})"
        
        elif ast[0] == 'le':
            return f"({linearize(ast[1])} <= {linearize(ast[2])})"
        
        elif ast[0] == 'seq':
            return f"{linearize(ast[1])} ;; {linearize(ast[2])}"
        
        elif ast[0] == 'nil':
            return "#"
        
        elif ast[0] == 'tl':
            # Don't evaluate again, just format what we have
            if isinstance(ast[1], tuple) and ast[1][0] == 'var':
                return f"(tl {ast[1][1]})"  # Format unevaluated tl of variable
            elif isinstance(ast[1], tuple) and ast[1][0] == 'cons':
                return linearize(evaluate(ast))  # Evaluate and linearize the result
            return f"(tl {linearize(ast[1])})"  # Format other unevaluated tl expressions

    return str(ast)

def evaluate(tree):
    if isinstance(tree, (float, int)):
        return tree

    if isinstance(tree, tuple):
        if tree[0] == 'lam':
            # If the lambda body is a constant value, return it directly
            body = evaluate(tree[2])
            if isinstance(body, (float, int)):
                return body
            return ('lam', tree[1], body)

        elif tree[0] == 'app':  
            if len(tree) == 2:  
                return evaluate(tree[1])  
            else:  
                left = evaluate(tree[1])  
                right = evaluate(tree[2])  
                
                # If left is nil, just return nil
                if isinstance(left, tuple) and left[0] == 'nil':
                    return left
                
                # If left is a lambda, then perform beta reduction  
                if isinstance(left, tuple) and left[0] == 'lam':  
                    substituted = substitute(left[2], left[1], right)  
                    return evaluate(substituted)  
       
                # Otherwise, preserve the application structure  
                return ('app', left, right)

        elif tree[0] == 'let':
            # Evaluate the value first
            value = evaluate(tree[2])
            # Then substitute it in the body and evaluate
            substituted = substitute(tree[3], tree[1], value)
            return evaluate(substituted)

        elif tree[0] == 'cons':
            # Simply evaluate both parts fully
            head = evaluate(tree[1])
            tail = evaluate(tree[2])
            return ('cons', head, tail)

        elif tree[0] == 'multiply':
            # Evaluate multiplication first
            left = evaluate(tree[1])
            right = evaluate(tree[2])
            if isinstance(left, (float, int)) and isinstance(right, (float, int)):
                return left * right
            return ('multiply', left, right)

        elif tree[0] == 'plus':
            left = evaluate(tree[1])
            right = evaluate(tree[2])
            if isinstance(left, (float, int)) and isinstance(right, (float, int)):
                return left + right
            return ('plus', left, right)

        elif tree[0] == 'minus':
            left = evaluate(tree[1])
            right = evaluate(tree[2])
            if isinstance(left, (float, int)) and isinstance(right, (float, int)):
                return left - right
            return ('minus', left, right)

        elif tree[0] == 'var':
            return tree

        elif tree[0] == 'number':
            return tree[1]

        elif tree[0] == 'negation':
            value = evaluate(tree[1])
            if isinstance(value, (float, int)):
                return -value
            return ('negation', value)
        
        elif tree[0] == 'rec':
            # For letrec, we use the Y combinator approach
            # Create a lambda that will be the recursive function
            func = ('lam', tree[1], tree[2])
            # Create the fix expression
            fix_expr = ('fix', func)
            # Evaluate the fix expression and substitute into body
            rec_value = evaluate(fix_expr)
            substituted = substitute(tree[3], tree[1], rec_value)
            return evaluate(substituted)

        elif tree[0] == 'fix':
            # Evaluate the argument to fix
            arg = evaluate(tree[1])
            if isinstance(arg, tuple) and arg[0] == 'lam':
                # Apply the function to (fix function)
                fix_point = ('app', arg, tree)
                return evaluate(fix_point)
            return ('fix', arg)

        elif tree[0] == 'if':
            condition = evaluate(tree[1])
            if isinstance(condition, tuple):
                # If condition didn't evaluate to a boolean/number, return the if expression
                return ('if', condition, tree[2], tree[3])
            if condition:
                return evaluate(tree[2])  # then branch
            else:
                return evaluate(tree[3])  # else branch

        elif tree[0] == 'eq':
            # First fully evaluate both sides to get complete lists
            left = evaluate(tree[1])
            right = evaluate(tree[2])
            
            # Compare the evaluated expressions
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return float(left == right)
            
            # For lists (cons structures), compare them recursively
            if isinstance(left, tuple) and isinstance(right, tuple):
                # If both are nil, they're equal
                if left[0] == 'nil' and right[0] == 'nil':
                    return float(True)
                # If both are cons cells, compare heads and tails
                if left[0] == 'cons' and right[0] == 'cons':
                    # First check if heads are equal
                    head_eq = evaluate(('eq', left[1], right[1]))
                    if head_eq == 0.0:  # If heads are not equal
                        return 0.0
                    # Then check if tails are equal
                    return evaluate(('eq', left[2], right[2]))
                return float(False)  # Different types of structures
            return float(False)  # Different types

        elif tree[0] == 'lt':
            left = evaluate(tree[1])
            right = evaluate(tree[2])
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left < right
            return ('lt', left, right)

        elif tree[0] == 'gt':
            left = evaluate(tree[1])
            right = evaluate(tree[2])
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left > right
            return ('gt', left, right)

        elif tree[0] == 'ge':
            left = evaluate(tree[1])
            right = evaluate(tree[2])
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left >= right
            return ('ge', left, right)

        elif tree[0] == 'le':
            left = evaluate(tree[1])
            right = evaluate(tree[2])
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left <= right
            return ('le', left, right)

        elif tree[0] == 'seq':
            # Evaluate both expressions and combine their results
            result1 = evaluate(tree[1])
            result2 = evaluate(tree[2])
            return ('seq', result1, result2)  # Keep original 'seq' tag

        elif tree[0] == 'hd':
            print("EVALUATING HD:", tree)
            lst = evaluate(tree[1])
            print("LIST TO TAKE HEAD FROM:", lst)
            if isinstance(lst, tuple):
                if lst[0] == 'cons':
                    head = lst[1]
                    print("HEAD VALUE:", head)
                    return head  # Simply return the head value
                elif lst[0] == 'nil':
                    return ('nil',)
            return ('hd', lst)  # Keep hd unevaluated for variables or other types

        elif tree[0] == 'tl':
            lst = evaluate(tree[1])
            if isinstance(lst, tuple):
                if lst[0] == 'cons':
                    return lst[2]  # Return the tail of the list
                elif lst[0] == 'nil':
                    return ('nil',)
            return ('tl', lst)  # Keep tl unevaluated for variables or other types

        elif tree[0] == 'nil':
            return ('nil',)

    return tree

# generate a fresh name 
# needed eg for \y.x [y/x] --> \z.y where z is a fresh name)
class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        # user defined names start with lower case (see the grammar), thus 'Var' is fresh
        return 'Var' + str(self.counter)

name_generator = NameGenerator()

# for beta reduction (capture-avoiding substitution)
def substitute(tree, name, replacement):
    if isinstance(tree, (float, int)):
        return tree
        
    if isinstance(tree, tuple):
        if tree[0] == 'var':
            if tree[1] == name:
                return replacement
            return tree
            
        elif tree[0] == 'lam':
            if tree[1] == name:
                # Don't substitute if the lambda binds the same name
                return tree
            elif isinstance(replacement, tuple) and replacement[0] == 'var':
                # If replacing with a variable, proceed normally
                body = substitute(tree[2], name, replacement)
                return ('lam', tree[1], body)
            else:
                # If replacing with a value, substitute directly
                body = substitute(tree[2], name, replacement)
                return ('lam', tree[1], body)
                
        elif tree[0] in ['app', 'plus', 'minus', 'multiply', 'cons']:
            return (tree[0], substitute(tree[1], name, replacement), 
                   substitute(tree[2], name, replacement))
            
        elif tree[0] == 'negation':
            return (tree[0], substitute(tree[1], name, replacement))
            
        elif tree[0] == 'number':
            return tree
            
        elif tree[0] == 'let':
            if tree[1] == name:
                return tree
            return ('let', tree[1], 
                    substitute(tree[2], name, replacement),
                    substitute(tree[3], name, replacement))

        elif tree[0] == 'rec':
            if tree[1] == name:
                return tree
            return ('rec', tree[1],
                    substitute(tree[2], name, replacement),
                    substitute(tree[3], name, replacement))

        elif tree[0] == 'fix':
            return ('fix', substitute(tree[1], name, replacement))
        
        elif tree[0] == 'if':
            return ('if',
                    substitute(tree[1], name, replacement),
                    substitute(tree[2], name, replacement),
                    substitute(tree[3], name, replacement))
        
        elif tree[0] in ['eq', 'lt', 'gt', 'le', 'ge']:
            return (tree[0],
                    substitute(tree[1], name, replacement),
                    substitute(tree[2], name, replacement))
    
    return tree

def main():
    input = sys.argv[1]
    result = interpret(input)
    print(f"\033[95m{result}\033[0m")

if __name__ == "__main__":
    main()