# sCKeme

**sCKeme** is a minimal, functional, LISP-like programming language implemented in Python. 
It is most closely inspired by Racket as this is what we learn in first year at UW (and thus Scheme, hence the name). 

I wanted to implement lazy evaluation, lambda functions, and simple first-class function support.

To help debug I changed it to eager evaluation, and fixed everything else.
I will convert it back to lazy soon, I have a simple Thunk class to help with this...
Then will finish expanding it.

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

1. Bring back lazy evaluation. I want call-by-need too so infinite data-types/streams etc. will all work.
2. Add lists and functional standard functions like map, append (maybe ++ like in Haskell?), foldl, foldr, car, cdr, etc...
3. Typing, and type hints
4. Tail call optimization

### Ecosystem

1. Emit LLVM code
2. Optimize and provide an LLVM compiler.