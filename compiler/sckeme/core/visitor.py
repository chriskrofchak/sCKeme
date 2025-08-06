from lark import Lark, Transformer, v_args
from core.ck_ast import *

@dataclass
class TempElseArm:
    arm: Expr

@v_args(inline=True)
class SCKemeTransformer(Transformer):
    def __init__(self, visit_tokens = True):
        super().__init__(visit_tokens)

    def start(self, *args):
        return Statements(args)

    def number(self, token) -> 'Float | Integer':
        return Float(float(token)) if '.' in token else Integer(int(token))

    def string(self, token):
        return String(token[1:-1])  # Strip quotes

    def var(self, token):
        return Var(str(token))

    def fun_def_head(self, *items):
        # x:xs = ... basically. 
        # I love Python...
        name, *params = list(map(str, items))
        return Signature(name = name, params = params)

    def lambda_expr(self, *items):
        *params, body = items
        return Lambda(params=[str(p) for p in params], body=body)

    def def_expr(self, head: 'Var | Signature', value: Expr):
        assert isinstance(head, Var) or isinstance(head, Signature), "DefExpr head parsed incorrectly."
        return Definition(name = head.name, signature=head if isinstance(head, Signature) else None, value=value)

    def cond_branch(self, test, result):
        return CondBranch(test=test, result=result)

    def else_arm(self, expr):
        return TempElseArm(expr)

    def cond_expr(self, *args):
        if isinstance(args[-1], TempElseArm):
            *branches, else_branch = args
            assert isinstance(else_branch, TempElseArm), "ElseBranch parsed incorrectly."
            else_branch: TempElseArm = else_branch
            return Conditional(branches=list(branches), else_branch=else_branch.arm)
        # else 
        return Conditional(branches = list(args))

    def call(self, first, *rest):
        assert isinstance(first, (Var, Lambda, Call)), "Parsed call function name wrong. Should be a Var, Lambda, or left rec. Call."
        return Call(func=first, args=list(rest))

class SCKemeParser:
    def __init__(self, grammar_file = "sckeme.lark", **options):
        with open(grammar_file, 'r') as f:
            grammar = f.read()
        self.parser = Lark(grammar = grammar, parser = 'lalr', transformer = SCKemeTransformer(), **options)

    def parse(self, code: str):
        return self.parser.parse(code)

class Visitor:
    def visit(self, node):
        method = getattr(self, f'visit_{type(node).__name__}', self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No visit_{type(node).__name__} method")
