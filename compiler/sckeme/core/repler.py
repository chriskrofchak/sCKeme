from core.visitor import SCKemeParser
from core.ck_ast import Statements, Expr
from core.interpreter import Interpreter
from core.constants import V, V_DATE, N_CACHE

def cache_results(intptr: Interpreter, last_value, n: int):
    # trickle up the cached variables
    for i in range(n, 1, -1):
        intptr.env.set(f'${i}', intptr.env.get(f'${i - 1}'))

    # cache previous value
    intptr.env.set('$1', last_value)

class Repler:
    def __init__(self):
        self.parser = SCKemeParser()
        self.intptr = Interpreter()
        # for cached return values...
        # to-do: remove for from files, but I'm keeping for my demo
        self.i: int = 0

    def interpret_expr(self, statement: Expr, raise_exceptions = False):
        line = statement
        try:
            value = self.intptr.visit(line)
        except Exception as e:
            print(repr(e))
            if raise_exceptions:
                raise e
            value = None
        if value is not None:
            self.i = min(self.i+1, N_CACHE)
            print(">", value)
            cache_results(self.intptr, value, self.i) # cache previous result(s)

    def repl(self):
        print("Welcome to SCKeme, a CK language.")
        print(f"--- v{V} as of {V_DATE}")
        parser = self.parser
        self.i = 0 # restart cache...
        while True:
            code = input(">>>")
            if code.strip() == 'exit()':
                break
            parsed_tree = parser.parse(code)
            assert isinstance(parsed_tree, Statements)
            assert len(parsed_tree.statements) == 1
            self.interpret_expr(parsed_tree.statements[0])

    def repl_from_file(self, path: str):
        with open(path, "r") as f:
            code = f.read()
        parsed_tree = self.parser.parse(code)
        assert isinstance(parsed_tree, Statements)
    
        self.i = 0
        for stmt in parsed_tree.statements:
            print(stmt)
            self.interpret_expr(stmt, raise_exceptions=True)
