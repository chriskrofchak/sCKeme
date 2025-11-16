from core.visitor import Visitor
from dataclasses import dataclass, field
from typing import Optional, Union
from copy import deepcopy

####################
## TYPES
####################

class CKType:
    def __truediv__(self, right):
        if isinstance(right, TypeVar):
            return VarSubstitution(t = self, a = right)
        else:
            raise ValueError(f"Division only supported between a t: CKType / a: TypeVar, denoting substituting t for a. Got {type(right)}.")

    def __getitem__(self, index) -> 'CKType':
        # so we can recur on next etc...
        if index is None:
            return self
        if isinstance(index, Substitution):
            ## recur on many
            if isinstance(index, CompositeSubstitution):
                return (self[index.curr])[index.next]
            
            ## actual substitution
            if isinstance(index, EmptySubstitution):
                return self
            assert isinstance(index, VarSubstitution)

            if is_primitive(self):
                return self
            if isinstance(self, TypeVar):
                return index.t if self == index.a else self
            
            assert isinstance(self, Func), f"Type {self} not supported yet..."
            return Func(t1 = self.t1[index], t2 = self.t2[index])
        else:
            raise ValueError(f"Substitution only supported for t2: CKType[s: Substition], denoting applying substitution s in t2. Got {type(index)}.")
    
    @property
    def kind(self):
        return self.__class__.__name__

    def __eq__(self, value):
        if not isinstance(value, CKType): return False
        return self.kind == value.kind

    def __str__(self):
        return f"{self.kind}"

@dataclass
class Int(CKType):
    pass

@dataclass
class Fl(CKType):
    pass

@dataclass
class Str(CKType):
    pass

@dataclass
class TypeVar(CKType):
    name: str

    def __eq__(self, value):
        if not isinstance(value, TypeVar): return False
        return self.name == value.name

    def __str__(self):
        return self.name

@dataclass
class Func(CKType):
    t1: CKType
    t2: CKType

    def __eq__(self, value):
        if not isinstance(value, Func): return False
        return self.t1 == value.t2 and self.t2 == value.t2

    def unpack(self):
        return self.t1, self.t

    def __str__(self):
        # b = lambda t: f"({str(t)})" if isinstance(t, Func) else f"{str(t)}"
        b = str
        return f"{b(self.t1)} -> {b(self.t2)}"

####################
## HM Type Inferencce
####################

### Substitution 
class Substitution:
    pass

@dataclass
class EmptySubstitution(Substitution):
    def __str__(self):
        return '[e-sub]'

@dataclass
class CompositeSubstitution(Substitution):
    curr: 'VarSubstitution'
    next: 'Union[CompositeSubstitution, EmptySubstitution]' = field(default_factory=EmptySubstitution)

    def __mul__(self, right):
        if isinstance(right, VarSubstitution):
                return CompositeSubstitution(curr = deepcopy(right), next = deepcopy(self))
        else:
            raise ValueError(f"Composition S1: CompSub * S2: VarSub only supported between CompSub x VarSub types, got {type(right)}.")


@dataclass
class VarSubstitution(Substitution):
    t: CKType
    a: TypeVar

    def __mul__(self, right):
        if isinstance(right, VarSubstitution):
                return CompositeSubstitution(curr = deepcopy(right), next = deepcopy(self))
        else:
            raise ValueError(f"Composition S1: VarSub * S2: VarSub only supported between VarSubstitution types, got {type(right)}.")

    def __str__(self):
        return f'[{str(self.t)}/{str(self.a)}]'

# Visitor over types
class Substitutor:
    pass

def is_primitive(t: CKType):
    return t.kind in { 'Int', 'Fl', 'Str' }

def is_type_var(t: CKType | TypeVar):
    return isinstance(t, TypeVar)

def occurs(a: TypeVar, tau: CKType):
    if is_primitive(tau):
        return False
    if is_type_var(tau):
        return a == tau
    assert isinstance(tau, Func), f"Should be a primitive type, a typevar or Func... got {tau}"
    return occurs(a, tau.t1) or occurs(a, tau.t2)

### Unification 
def U(t1: CKType, t2: CKType):
    if is_primitive(t1) or is_primitive(t2):
        if t1 == t2:
            return EmptySubstitution()
        raise TypeError(f"{t1} and {t2} incompatible types.")
    # so either t1 or t2 are func types
    if isinstance(t1, Func) and isinstance(t2, Func):
        t1l, t1r = t1.unpack() # t1 unpacked into t1l -> t1r
        t2l, t2r = t2.unpack() # t2 unpacked into t2l -> t2r
        S1 = U(t1l, t2l)
        S2 = U(t1r[S1], t2r[S1]) # use substitution S1 in types t1r, t2r
        return S1 * S2
    # or we have a type and a type variable
    if is_type_var(t1) or is_type_var(t2):
        a   = t1 if is_type_var(t1) else t2
        tau = t2 if is_type_var(t1) else t1
        # if a occurs in tau, error else [tau/a]
        if occurs(a, tau):
            raise TypeError(f"{a} not fresh in {tau}, cannot unify types.")
        # else
        return tau / a # creates substitution
    raise TypeError(f"No path to unify {t1}, and {t2}.")


### Algorithm W
class W(Visitor):
    pass