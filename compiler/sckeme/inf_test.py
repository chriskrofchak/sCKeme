from core.inference import *

if __name__ == "__main__":
    t = Func(TypeVar('a'), TypeVar('a'))
    print(t)
    print(Func(t, TypeVar('b')))
    print(t[Int() / TypeVar('a')])
    s1 = Int() / TypeVar('a')
    s2 = Fl() / TypeVar('b')
    print(Func(t, TypeVar('b'))[s2 * s1])
    print(TypeVar('a')[Int() / TypeVar('a')])
    print(Int()[Fl() / TypeVar('a')])