# from core.ck_ast import Definition
# from core.thunk import Thunk
from typing import Optional
# from functools import reduce

class Env:
    def __init__(self, dict = None, parent = None):
        self.bindings = dict or {}
        self.parent: 'Optional[Env]' = parent

    def extend(self):
        return Env(parent=self)

    def __getitem__(self, name):
        if name in self.bindings:
            return self.bindings[name]
        elif self.parent:
            return self.parent[name]
        else:
            raise NameError(f"Unbound variable: {name}")

    def __setitem__(self, name, value):
        self.bindings[name] = value

    def __contains__(self, name):
        return name in self.bindings or (self.parent and name in self.parent)

    def __or__(self, value):
        new_env = self.extend()
        new_env.update(value)
        return new_env

    def update(self, other: 'Env'):
        if not isinstance(other, Env):
            raise TypeError(f"Can only update an environment with another environment. {type(other)}, {other}")
        self.bindings.update(other.bindings)

    def set(self, name, value):
        self[name] = value

    def get(self, name):
        return self[name] # we have __getitem__

    def to_dict(self):
        return (self.parent.to_dict() if self.parent else {}) | self.bindings

    def keys(self):
        return (self.parent.keys() if self.parent else set()) | self.bindings.keys()

    def __str__(self):
        return f"Env({self.to_dict()})"
