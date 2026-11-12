from core.ck_ast import Expr, Literal, BaseInterpreter
from core.ck_env import Env
from enum import Enum

class _Force(Enum):
    UNFORCED = 0
    FORCED = 1
    EVALUATING = 2


class Thunk:
    def __init__(self, expr: Expr, env: Env, why = None):
        # print("Thunking:", expr, f"(why = {why})" if why else "")
        self.expr    = expr
        self.literal = isinstance(expr, Literal)
        self.env     = env if not self.literal else Env() # empty env if literal
        self._value  = expr.value if isinstance(expr, Literal) else None 
        self._forced: _Force = _Force.FORCED if self.literal else _Force.UNFORCED

    def __repr__(self):
        return (
            f"Thunk({self._value})" if self._forced else
            f"Thunk(expr = {self.expr}, env = {self.env})"
        )

    # interpreter should be an interpreter class
    def force(self, interpreter: BaseInterpreter):
        if self._forced == _Force.EVALUATING:
            raise ValueError("Black-holed.")
        # else.
        if self._forced == _Force.UNFORCED:
            self._forced = _Force.EVALUATING
            # print("thunking", self.expr)
            # print("  with:", self.env)
            # assert 1 == 3, "here 1 == 3"
            # print("Forcing thunk:", self.expr, f"(is_literal: {self.literal})")
            try:
                self._value  = interpreter.visit_with_env(self.expr, self.env)
                self._forced = _Force.FORCED
            except BaseException as e:
                self._forced = _Force.UNFORCED # computation failed
                raise e # re-raise
        return self._value
        
