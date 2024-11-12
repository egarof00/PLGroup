import sys
from lark import Lark, Transformer, Tree
import lark

print(f"Python version: {sys.version}")
print(f"Lark version: {lark.__version__}")

#  run/execute/interpret source code
def interpret(source_code):
    print("SOURCE: ")
    print(source_code)
    print()
    cst = parser.parse(source_code)
    print(cst)
    print()
    ast = LambdaCalculusTransformer().transform(cst)
    print(ast)
    result_ast = evaluate(ast)
    result = linearize(result_ast)
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

def linearize(ast):
    if isinstance(ast, (float, int)):
        return f"{ast:.1f}"
    
    # If it can't be fully evaluated, format it appropriately
    if isinstance(ast, tuple):
        if ast[0] == 'var':
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
    
    return str(ast)

def evaluate(tree):
    if isinstance(tree, (float, int)):
        return tree

    if isinstance(tree, tuple):
        if tree[0] == 'app':
            # Only evaluate the left side of the application
            left = evaluate(tree[1])
            
            # If left is a lambda, then perform beta reduction
            # but DON'T evaluate the right side first
            if isinstance(left, tuple) and left[0] == 'lam':
                # Remove evaluation of right side here
                substituted = substitute(left[2], left[1], tree[2])
                return evaluate(substituted)
            
            # Otherwise, preserve the application structure
            return ('app', left, tree[2])

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

        elif tree[0] == 'lam':
            return tree

        elif tree[0] == 'var':
            return tree

        elif tree[0] == 'number':
            return tree[1]

        elif tree[0] == 'negation':
            value = evaluate(tree[1])
            if isinstance(value, (float, int)):
                return -value
            return ('negation', value)

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
                return tree
            else:
                fresh_name = name_generator.generate()
                body = substitute(tree[2], tree[1], ('var', fresh_name))
                body = substitute(body, name, replacement)
                return ('lam', fresh_name, body)
                
        elif tree[0] in ['app', 'plus', 'minus', 'multiply']:
            return (tree[0], substitute(tree[1], name, replacement), 
                   substitute(tree[2], name, replacement))
            
        elif tree[0] == 'negation':
            return (tree[0], substitute(tree[1], name, replacement))
            
        elif tree[0] == 'number':
            return tree
            
    return tree

def main():
    input = sys.argv[1]
    result = interpret(input)
    print(f"\033[95m{result}\033[0m")

if __name__ == "__main__":
    main()