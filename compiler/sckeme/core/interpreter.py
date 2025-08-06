from core.visitor import Visitor
from core.ck_ast import *
from functools import reduce
from core.thunk import Thunk
from core.ck_env import Env
from core.closure import Closure

@dataclass
class BuiltinOp:
    op: str

class Builtin:
    ops = {
        '+':     lambda *args: sum(args),
        '*':     lambda *args: reduce(lambda l, r: l*r, args, 1),
        '-':     lambda l, r: l - r,
        '/':     lambda l, r: l / r,
        '//':    lambda l, r: l // r,
        '=':     lambda l, r: l == r,
        '!=':    lambda l, r: l != r,
        '>':     lambda l, r: l > r,
        '<':     lambda l, r: l < r,
        '>=':    lambda l, r: l >= r,
        '<=':    lambda l, r: l <= r,
        "print": lambda *args: print(args)
    }

    def __init__(self):
        pass

    def __contains__(self, name):
        return name in self.ops

    def eval(self, op: BuiltinOp, *args):
        return self.ops[op.op](*args)

class Interpreter(Visitor):
    def __init__(self, env=None):
        self.ops = Builtin()
        self.env = env or Env()

    def visit_Integer(self, node: Integer):
        return node.value

    def visit_Float(self, node: Float):
        return node.value

    def visit_String(self, node: String):
        return node.value

    def visit_Var(self, node: Var):
        if node.name in self.ops:
            return BuiltinOp(node.name)
        else:
            value = self.env.get(node.name)
            if isinstance(value, Definition):
                return Closure(value.signature.params, value.value, self.env) if value.signature else self.visit(value.value) # value def
            elif isinstance(value, (int, float, str, Closure)):
                return value
            else:
                raise ValueError(f"Can't interpret the type, {type(value)}, of {repr(value)}")

    def visit_Definition(self, node: Definition):
        self.env.set(node.name, node)
        return None

    def visit_Lambda(self, node: Lambda):
        # Capture current env to form closure
        return Closure(params=node.params, body=node.body, env=self.env)

    def visit_Call(self, node: Call):
        func = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
    
        if not isinstance(func, (Closure, BuiltinOp)):
            raise TypeError(f"Tried to call non-function: {func}")

        if isinstance(func, BuiltinOp):
            self.args = args # will catch it in visit_BuiltinOp
            return self.visit(func)

        # else 
        assert isinstance(func, Closure)
        self.args = args
        return self.visit(func)

    def visit_BuiltinOp(self, node: BuiltinOp):
        return self.ops.eval(node, *self.args)

    # TO-DO, refactor nicely into a visit_Closure class
    def visit_Closure(self, node: Closure):
        func = node
        args = self.args
        local_env = func.env.extend()
        for param, arg_val in zip(func.params, args):
            local_env.set(param, arg_val)

        return self.visit_with_env(func.body, local_env)

    def visit_CondBranch(self, node: CondBranch):
            return CondBranch(
                test=self.visit(node.test),
                result=self.visit(node.result)
            )

    def visit_Conditional(self, node: Conditional):
        for branch in node.branches:
            if self.visit(branch.test):
                return self.visit(branch.result)
        return self.visit(node.else_branch) if node.else_branch else None

    def visit_with_env(self, node, env):
        old_env = self.env
        self.env = env
        try:
            return self.visit(node)
        finally:
            self.env = old_env