import sys
from core.repler import Repler

USAGE = "usage: uv run repl.py [file.sck]"

def main() -> None:
    repler = Repler()
    args = sys.argv[1:]
    if len(args) > 1:
        sys.exit(USAGE)
    if args:
        # uv run repl.py tests/foo.sck: run a file, keep going after errors
        try:
            repler.repl_from_file(args[0], stop_on_error=False)
        except OSError as e:
            sys.exit(f"can't open {args[0]}: {e.strerror}")
    elif not sys.stdin.isatty():
        # uv run repl.py < tests/foo.sck: same as running the file
        repler.run_source(sys.stdin.read(), stop_on_error=False)
    else:
        repler.repl()

if __name__ == "__main__":
    main()
