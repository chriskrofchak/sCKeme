# sCKeme

**sCKeme** is a minimal, functional, LISP-like programming language implemented in Python. 
It is most closely inspired by Racket as this is what we learn in first year at UW (and thus Scheme, hence the name). 

It has lazy evaluation, lambda functions, and simple first-class function support.

I will need to do more rigorous testing to make sure my thunking/forcing is not wasteful, and thunking is happening reasonably once, when needed, and then forcing happens whenever it is needed. Looking at the print statements I see that thunking happens repeatedly in recursive calls. I may be able to optimize this away.

This repo includes:

- A **Python interpreter** for sCKeme.
- A starter **LLVM pass** (hello-world style) that will be integrated with the IR backend in future stages.

---

## Features

- LISP-like syntax: `(op arg1 arg2 ...)`
- `def` for variable and function definitions
- First-class lambdas: `(lambda (x) (+ x 2))`
- Lexical scoping and closures
- `cond` for conditional branching
- Recursion
- REPL environment, caches previous return value in variable name `$1` to help with debugging.
- Lazy evaluation

Example:

```lisp
(def (make-multiplier x)
  (lambda (y) (* x y)))

(def (times2 x) ((make-multiplier 2) x))

(times2 5)
; Outputs:
; > 10 

(def (square n) (cond [(<= n 0) 0]
                 else (+ (- (* 2 n) 1) (square (- n 1)))))

(def tea 24)
(square tea)
; Outputs:
; > 576

```

## TO-DO

### Language 

1. Tail call optimization.
2. Add lists and functional standard functions like map, append (maybe ++ like in Haskell?), foldl, foldr, car, cdr, etc...
3. Typing, and type hints.

### Ecosystem

1. Emit LLVM code
2. Optimize and provide an LLVM compiler.

## Changelog

### As of 2025-11-16.
To help debug I changed it to eager evaluation, and fixed everything else, now:
* I have added the Thunk class back in, so now arguments when passed to closures are lazy.
* When passed to builtin functions like addition and so on, it is eager, since they should all be evaluated regardless.
* Added up to 10 previous arguments with the `$#` operator in REPL.
* Refactored "REPL" into a Repler class. Reused for files and command line... To-do they actually should probably be different.