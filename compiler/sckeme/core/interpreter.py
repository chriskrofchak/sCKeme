from core.visitor import Visitor
from core.ck_ast import *
from functools import reduce
from core.thunk import Thunk
from core.ck_env import Env
from core.closure import Closure

class Caller(Visitor):
    def __init__(self, interpreter: 'Interpreter', env: Env, args: list = None):
        super().__init__()
        self.interpreter = interpreter
        self.env         = env
        self.args        = args

    def __repr__(self):
        return f"Caller(args = {repr(self.args)})"

    def _visit_helper(self, params, value):
        args = self.args
        if len(params) != len(args):
                raise TypeError(f"Expected {len(params)} args, got {len(args)}")

        # wrap local environment,
        # to save on recursion, we never thunk Definitions
        local_env = Env(dict = {
            param: (arg_expr if isinstance(arg_expr, Definition) else
                    Thunk(arg_expr, self.env))
            for param, arg_expr in zip(params, args)
        }, parent = value.env if isinstance(value, Closure) else self.env) # needs parent to shadow

        if isinstance(value, Closure) and isinstance(value.body, Call):
            # have already replaced all the closures, just execute the body.
            return self.interpreter.visit_with_env(value.body, local_env | value.env)

        # else recur and prepare to force
        return self.interpreter.visit_with_env(value, local_env)

    def visit_Definition(self, node: Definition):
        # has the function, just call it with the parameters, 
        # the args are initialized in Caller
        # if a lambda is defined we need to visit it 
        # to make it a closure so that it will be "forced"
        # value = self.interpreter.visit(node.value) if isinstance(node.value, Lambda) else node.value
        value = node.value
        return self._visit_helper(params = node.signature.params, value = value)

    # def visit_Call(self, node: Call):
    #     func_val = (
    #         self.env[node.func.name]
    #         if isinstance(node.func, Var)
    #         else self.interpreter.visit_with_env(node.func, self.env)
    #     )

    #     # Convert Definition to Closure at call time
    #     if isinstance(func_val, Definition):
    #         func_val = Closure(
    #             params=func_val.signature.params,
    #             body=func_val.value,
    #             env=self.env  # capture caller's env
    #         )

    #     # Apply Closure
    #     if isinstance(func_val, Closure):
    #         expected = len(func_val.params)
    #         given = len(self.args)

    #         # to do : allow partial application
    #         if given != expected:
    #             raise TypeError(f"Function expects {expected} arguments, but got {given}")

    #         # All args present — apply
    #         local_env = func_val.env.extend()
    #         for param, arg in zip(func_val.params, self.args):
    #             local_env[param] = Thunk(arg, self.env)

    #         return self.interpreter.visit_with_env(func_val.body, local_env)

    #     raise TypeError(f"Attempted to call non-callable: {func_val}")

    def visit_Closure(self, node: Closure):
        shadow = self.env
        self.env = node.env
        try:
            value = self._visit_helper(params = node.params, value = node.body)
        finally:
            self.env = shadow
            return value

class Interpreter(Visitor):
    def __init__(self):
        self.env: 'Env' = Env()

    def visit_with_env(self, expr: Expr, env: Env):
        old_env = self.env
        self.env = env  # just set it
        try:
            return self.visit(expr)
        finally:
            self.env = old_env

    def visit_Integer(self, node: Integer):
        return node.value

    def visit_Float(self, node: Float):
        return node.value

    def visit_String(self, node: String):
        return node.value

    def visit_Var(self, node: Var):
        if node.name in self.env:
            value = self.env[node.name]
            if isinstance(value, Thunk):
                return value.force(self)
            return self.visit(value.value) if isinstance(value, Definition) else value
        raise NameError(f"Undefined variable: {node.name}")

    def visit_Definition(self, node: Definition):
        self.env[node.name] = node
        return None

    def visit_Lambda(self, node: Lambda):
        return Closure(params = node.params, body = node.body, env = self.env)

    def visit_Call(self, node: Call):
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
        # defined functions... "supported"?
        if isinstance(node.func, Var) and node.func.name in ops:
            evaluated_args = list(map(lambda arg: Thunk(arg, self.env).force(self), node.args))
            return ops[node.func.name](*evaluated_args)

        # user defined functions
        if isinstance(node.func, Lambda) or isinstance(node.func, Call) or node.func.name in self.env:
            # have to wrap it into a closure, telling it we are ready to force it.
            callee: Definition | Lambda | Call = self.visit(node.func) if isinstance(node.func, (Lambda, Call)) else self.env[node.func.name]
            return Caller(interpreter = self, env = self.env, args = node.args).visit(callee)

        raise NameError(f"Calling function {node.func} which is not yet(?) in scope.")

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