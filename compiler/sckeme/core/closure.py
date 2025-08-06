from core.ck_ast import Expr
from core.ck_env import Env
from typing import List
from dataclasses import dataclass

@dataclass
class Closure:
    params: List[Expr]
    body: Expr
    env: Env
    
    def __repr__(self):
        return f"Closure(params = {self.params}, body = {repr(self.body)}, env = {self.env.keys()})"
    