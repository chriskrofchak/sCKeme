from core.ck_ast import Expr, Literal
from core.ck_env import Env

class Thunk:
    def __init__(self, expr: Expr, env: Env):
        self.expr    = expr
        self.literal = isinstance(expr, Literal)
        self.env     = env if not self.literal else None
        self._value  = expr.value if isinstance(expr, Literal) else None 
        self._forced = self.literal

    def __repr__(self):
        return (
            f"Thunk({self._value})" if self._forced else
            f"Thunk(expr = {self.expr}, env = {self.env})"
        )

    # interpreter should be an interpreter class
    def force(self, interpreter):
        if not self._forced:
            # print("thunking", self.expr)
            # print("  with:", self.env)
            # assert 1 == 3, "here 1 == 3"
            self._value  = interpreter.visit_with_env(self.expr, self.env)
            self._forced = True
        return self._value
