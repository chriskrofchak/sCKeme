from dataclasses import dataclass
from typing import List, Union, Optional
from core.ck_env import Env

class BaseInterpreter:
    # to be implemented in Interpreter
    def visit_with_env(self, env: Env):
        ...

@dataclass
class Expr:
    def __init__(self, *args):
        self.children = args

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.joini(list(map(repr, self.children)))})"

@dataclass
class Literal(Expr):
    value: Union[int, float, str]

    def __str__(self):
        return f"{self.value}"

@dataclass
class Number(Literal):
    value: Union[int, float]

@dataclass
class Integer(Number):
    value: int

@dataclass
class Float(Number):
    value: float

@dataclass
class String(Literal):
    value: str

    def __str__(self):
        return f'"{self.value}"'

@dataclass
class Signature:
    name: str
    params: List[str]

    def __str__(self):
        return ' '.join(list(map(str, self.params)))

@dataclass
class Lambda(Expr):
    params: List[str]
    body: Expr

    def __str__(self):
        return f"(lambda ({' '.join(list(map(str, self.params)))}) {str(self.body)})"

@dataclass
class Var(Expr):
    name: str

    def __str__(self):
        return self.name

@dataclass
class Definition(Expr):
    # If target is str => variable def
    # If target is tuple => function def: (name, [params])
    name:  str
    value: Expr
    signature: Optional[Signature] = None

    def __str__(self):
        return (
            f"(def ({str(self.name)} {str(self.signature)}) {str(self.value)})"
            if self.signature else
            f"(def {str(self.name)} {str(self.value)})"
        )

@dataclass
class CondBranch:
    test: Expr
    result: Expr

    def __str__(self):
        return f'[{self.test} {self.result}]'

@dataclass
class Conditional(Expr):
    branches: List[CondBranch]
    else_branch: Optional[Expr] = None

    def __str__(self):
        return f"(cond {' '.join(list(map(str, self.branches)))}{' else ' + str(self.else_branch) if self.else_branch else ''})"

@dataclass
class Call(Expr):
    func: Union[Var, Lambda, 'Call']
    args: List[Expr]

    def __str__(self):
        return f"({str(self.func)} {' '.join(list(map(str, self.args)))})"

@dataclass
class Statements:
    statements: List[Expr]