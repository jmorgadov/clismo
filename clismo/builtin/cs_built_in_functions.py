import builtins
import math
import random
from time import sleep

import clismo.exceptions as excpt
from clismo.lang.type import Type

__BUILTINS = {}

cs_float = Type.get("float")
cs_int = Type.get("int")
cs_str = Type.get("str")
cs_list = Type.get("list")
cs_bool = Type.get("bool")


def builtin_func(func_name):
    def deco(func):
        __BUILTINS[func_name] = func
        return func

    return deco


def resolve(func_name):
    return __BUILTINS.get(func_name, None)


@builtin_func("repr")
def cs_repr(arg):
    return arg.get("__repr__")(arg)


@builtin_func("print")
def cs_print(value, *args, sep=cs_str(" "), end=cs_str("\n")):
    values = [value.get("__str__")(value).get("value")] + [
        arg.get("__str__")(arg).get("value") for arg in args
    ]
    builtins.print(*values, sep=sep.get("value"), end=end.get("value"))


@builtin_func("abs")
def cs_abs(x: cs_float):
    return cs_float(builtins.abs(x.get("value")))


@builtin_func("bin")
def cs_bin(x: cs_int):
    return cs_str(builtins.bin(x.get("value")))


@builtin_func("pow")
def cs_pow(base, exp, mod):
    return cs_float(builtins.pow(base.get("value"), exp.get("value"), mod.get("value")))


@builtin_func("round")
def cs_round(x, ndigits=None):
    if ndigits is None:
        return cs_float(builtins.round(x.get("value")))
    return cs_float(builtins.round(x.get("value"), ndigits.get("value")))


@builtin_func("sum")
def cs_sum(iterable, start=cs_int(0)):
    if "__iter__" in iterable._dict:
        answ = None
        for item in iterable:
            if answ is None:
                answ = item
            else:
                answ = answ.get("__add__")(answ, item)
        return answ
    raise excpt.InvalidTypeError("sum() can't sum non-iterable")


@builtin_func("sorted")
def cs_sorted(iterable, key=None, reverse=cs_bool(False)):
    raise NotImplementedError("sorted() is not implemented yet")


@builtin_func("iter")
def cs_iter(x):
    return x.get("__iter__")(x)


@builtin_func("max")
def cs_max(a, *args):
    if args:
        answ = a
        for arg in args:
            answ = answ.get("__gt__")(answ, arg)
        return answ

    if "__iter__" in a._dict:
        answ = None
        for item in a:
            if answ is None:
                answ = item
            else:
                answ = answ.get("__gt__")(answ, item)
        return answ
    return a


@builtin_func("min")
def cs_min(a, *args):
    if args:
        answ = a
        for arg in args:
            answ = answ.get("__lt__")(answ, arg)
        return answ

    if "__iter__" in a._dict:
        answ = None
        for item in a:
            if answ is None:
                answ = item
            else:
                answ = answ.get("__lt__")(answ, item)
        return answ
    return a


@builtin_func("len")
def cs_len(x):
    return x.get("__len__")(x)


@builtin_func("hash")
def cs_hash(x):
    return x.get("__hash__")(x)


@builtin_func("input")
def cs_input():
    return cs_str(builtins.input())


@builtin_func("range")
def cs_range(start, stop=None, step=None):
    if stop is None:
        stop = start
        start = cs_int(0)
    if step is None:
        step = cs_int(1)

    def move_next(self):
        if not "current" in self._dict:
            self.set("current", start)
            return start
        old_current = self.get("current")
        self.set("current", old_current.get("__add__")(old_current, step))
        current = self.get("current")
        if current.get("__ge__")(current, stop).get("value"):
            raise StopIteration
        return current

    return Type.new("generator", move_next)


@builtin_func("rand")
def cs_rand():
    return cs_float(random.random())


@builtin_func("randint")
def cs_randint(a, b):
    return cs_int(random.randint(a.get("value"), b.get("value")))


@builtin_func("norm")
def cs_norm():
    return cs_float(random.normalvariate(0, 1))


@builtin_func("sqrt")
def cs_sqrt(x):
    return cs_float(math.sqrt(x.get("value")))


@builtin_func("sleep")
def cs_sleep(x: cs_float):
    return cs_float(sleep(x))


@builtin_func("log")
def log(x, base):
    return cs_float(math.log(x.get("value"), base.get("value")))


@builtin_func("log2")
def log2(x):
    return cs_float(math.log2(x.get("value")))


@builtin_func("exp")
def exp(x):
    return cs_float(math.exp(x.get("value")))


@builtin_func("ceil")
def ceil(x):
    return cs_int(math.ceil(x.get("value")))


@builtin_func("floor")
def floor(x):
    return cs_int(math.floor(x.get("value")))


@builtin_func("sin")
def sin(x):
    return cs_float(math.sin(x.get("value")))


@builtin_func("cos")
def cos(x):
    return cs_int(math.cos(x.get("value")))


@builtin_func("tan")
def tan(x):
    return cs_int(math.tan(x.get("value")))
