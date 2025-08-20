from inspect import currentframe
from types import SimpleNamespace


def get_namespace(args):
    caller_locals = currentframe().f_back.f_back.f_locals
    idmap = {id(variable): name for name, variable in caller_locals.items()}
    argids = {id(arg): arg for arg in args}
    ns = SimpleNamespace()
    for id_, arg in argids.items():
        if (name := idmap.get(id_)) is not None:
            ns.__dict__[name] = arg
    if currentframe().f_back.f_back.f_code.co_name != "<module>":
        caller_locals.clear()
    return ns


def f():
    a, b, c, d = 1, 2, 3, 4
    return g(a, b, c, d)


def g(*args):
    ns = get_namespace(args)
    return ns.a + ns.b + ns.c + ns.d


print(f())