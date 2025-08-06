from os import walk as os_walk
from core.visitor import SCKemeParser
from core.ck_ast import Statements
from core.interpreter import Interpreter






if __name__ == "__main__":
    prefix, _, files = next(os_walk('tests'))
    fails = set()
    for file in files:
        print("===", file)
        # if file != 'funcs.sck': continue # not ready
        with open(f"{prefix}/{file}", "r") as f:
            code = f.read()
        parser = SCKemeParser()
        parsed_tree = parser.parse(code)
        assert isinstance(parsed_tree, Statements)
        repler = Interpreter()
        for stmt in parsed_tree.statements:
            print(stmt)
            try:
                result = repler.visit(stmt)
                if result is not None:
                    print(">", result)
                    repler.env.set('$1', result) # cache previous result
            except Exception as e:
                print(f"FAILED IN {file} ON {stmt} WITH", repr(e))
                # raise e
                fails |= { file }
        else:
            print("PASSED", file)
    print("=== SUMMARY")
    for file in files:
        print(file, "FAILED..." if file in fails else "PASSED.")

        