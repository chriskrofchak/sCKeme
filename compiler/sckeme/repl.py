from os import walk as os_walk
from core.visitor import SCKemeParser
from core.ck_ast import Statements
from core.interpreter import Interpreter
from datetime import datetime

if __name__ == "__main__":
    print("Welcome to SCKeme, a CK language.")
    print(f"--- v0.0.1 as of {datetime.now().strftime('%c')}")
    parser = SCKemeParser()
    repler = Interpreter()
    while True:
        code = input("sCKeme>")
        parsed_tree = parser.parse(code)
        assert isinstance(parsed_tree, Statements)
        assert len(parsed_tree.statements) == 1
        line = parsed_tree.statements[0]
        value = repler.visit(line)
        if value:
            print(value)
        