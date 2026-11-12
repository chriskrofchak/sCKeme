from lark import UnexpectedInput, UnexpectedToken, UnexpectedCharacters, UnexpectedEOF
from core.visitor import SCKemeParser
from core.ck_ast import Statements, Expr
from core.interpreter import Interpreter
from core.constants import V, V_DATE, N_CACHE, PROMPT, CONT_PROMPT

def cache_results(intptr: Interpreter, last_value, n: int):
    # trickle up the cached variables
    for i in range(n, 1, -1):
        intptr.env.set(f'${i}', intptr.env.get(f'${i - 1}'))

    # cache previous value
    intptr.env.set('$1', last_value)

def is_end_of_input(e: UnexpectedInput) -> bool:
    # the parser ran out of input before the expression was finished, e.g. "(+ 1"
    return isinstance(e, UnexpectedEOF) or (isinstance(e, UnexpectedToken) and e.token.type == '$END')

def describe_syntax_error(e: UnexpectedInput) -> str:
    if is_end_of_input(e):
        return "syntax error: unexpected end of input (missing a closing paren?)"
    if isinstance(e, UnexpectedCharacters):
        return f"syntax error: unexpected character {e.char!r} at line {e.line}, column {e.column}"
    if isinstance(e, UnexpectedToken):
        return f"syntax error: unexpected {e.token.value!r} at line {e.line}, column {e.column}"
    return f"syntax error: {str(e).splitlines()[0]}"

def describe_error(e: Exception) -> str:
    return f"error: {e}" if str(e) else f"error: {type(e).__name__}"

class Repler:
    def __init__(self):
        self.parser = SCKemeParser()
        self.intptr = Interpreter()
        # for cached return values...
        # to-do: remove for from files, but I'm keeping for my demo
        self.i: int = 0

    def interpret_expr(self, statement: Expr, raise_exceptions = False):
        try:
            value = self.intptr.visit(statement)
        except Exception as e:
            print(describe_error(e))
            if raise_exceptions:
                raise e
            value = None
        if value is not None:
            self.i = min(self.i+1, N_CACHE)
            print(">", value)
            cache_results(self.intptr, value, self.i) # cache previous result(s)

    def repl(self):
        try:
            # importing readline is enough: input() then gets up/down history
            # and left/right line editing
            import readline  # noqa: F401
        except ImportError:
            pass  # e.g. on Windows: no history, everything else still works
        print("Welcome to SCKeme, a CK language.")
        print(f"--- v{V} as of {V_DATE}")
        self.i = 0 # restart cache...
        buffer = "" # lines of an expression that isn't finished yet
        while True:
            try:
                line = input(CONT_PROMPT if buffer else PROMPT)
            except EOFError: # Ctrl-D
                print()
                break
            except KeyboardInterrupt: # Ctrl-C throws away a half-typed expression
                print()
                buffer = ""
                continue
            if not buffer and line.strip() == 'exit()':
                break

            buffer += line + "\n"
            try:
                parsed_tree = self.parser.parse(buffer)
            except UnexpectedInput as e:
                if self.parser.is_blank(buffer):
                    buffer = ""  # only whitespace / comments, nothing to run
                elif not is_end_of_input(e):
                    print(describe_syntax_error(e))
                    buffer = ""
                # else: unfinished expression, keep reading lines into the buffer
                continue
            except Exception as e: # e.g. asserts in the transformer, like (1 2)
                print(describe_error(e))
                buffer = ""
                continue

            buffer = ""
            assert isinstance(parsed_tree, Statements)
            try:
                for stmt in parsed_tree.statements:
                    self.interpret_expr(stmt)
            except KeyboardInterrupt: # Ctrl-C stops a long-running evaluation
                print("\ninterrupted")

    def run_source(self, code: str, stop_on_error = True):
        # Echo each statement and its result. With stop_on_error=False, keep going
        # after errors so files full of expected errors can be read top to bottom.
        if self.parser.is_blank(code):
            return
        try:
            parsed_tree = self.parser.parse(code)
        except UnexpectedInput as e:
            print(describe_syntax_error(e))
            if stop_on_error:
                raise
            return
        assert isinstance(parsed_tree, Statements)

        self.i = 0
        for stmt in parsed_tree.statements:
            print(stmt)
            self.interpret_expr(stmt, raise_exceptions=stop_on_error)

    def repl_from_file(self, path: str, stop_on_error = True):
        with open(path, "r") as f:
            code = f.read()
        self.run_source(code, stop_on_error)
