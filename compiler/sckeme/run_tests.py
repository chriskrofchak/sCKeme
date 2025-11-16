from os import walk as os_walk
from core.repler import Repler


def main() -> None:
    prefix, _, files = next(os_walk('tests'))
    fails = set()
    repler = Repler()
    for file in files:
        print("===", file)

        try:
            repler.repl_from_file(f"{prefix}/{file}")
        except Exception as e:
            print(f"FAILED IN {file} WITH", repr(e))
            # raise e
            fails |= { file }
        else:
            print("PASSED", file)
    print("=== SUMMARY")
    for file in files:
        print(file, "FAILED..." if file in fails else "PASSED.")

if __name__ == "__main__":
    main()