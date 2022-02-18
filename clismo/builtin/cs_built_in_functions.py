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


def builtin_func(func_name, return_type):
    def deco(func):
        __BUILTINS[func_name] = (func, return_type)
        return func

    return deco


def resolve(func_name):
    return __BUILTINS.get(func_name, None)


#region Numeric Functions


@builtin_func("abs", cs_float)
def cs_abs(x: cs_float):
    return cs_float(builtins.abs(x.get("value")))


@builtin_func("bin", cs_str)
def cs_bin(x: cs_int):
    return cs_str(builtins.bin(x.get("value")))


@builtin_func("round", cs_float)
def cs_round(x, ndigits=None):
    if ndigits is None:
        return cs_float(builtins.round(x.get("value")))
    return cs_float(builtins.round(x.get("value"), ndigits.get("value")))


@builtin_func("rand", cs_float)
def cs_rand():
    return cs_float(random.random())


@builtin_func("randint", cs_str)
def cs_randint(a, b):
    return cs_int(random.randint(a.get("value"), b.get("value")))


@builtin_func("norm", cs_float)
def cs_norm():
    return cs_float(random.normalvariate(0, 1))


@builtin_func("sqrt", cs_float)
def cs_sqrt(x):
    return cs_float(math.sqrt(x.get("value")))


@builtin_func("sleep", cs_float)
def cs_sleep(x: cs_float):
    return cs_float(sleep(x))


@builtin_func("log", cs_float)
def log(x, base):
    return cs_float(math.log(x.get("value"), base.get("value")))


@builtin_func("log2", cs_float)
def log2(x):
    return cs_float(math.log2(x.get("value")))


@builtin_func("exp", cs_float)
def exp(x):
    return cs_float(math.exp(x.get("value")))


@builtin_func("ceil", cs_int)
def ceil(x):
    return cs_int(math.ceil(x.get("value")))


@builtin_func("floor", cs_int)
def floor(x):
    return cs_int(math.floor(x.get("value")))


@builtin_func("sin", cs_float)
def sin(x):
    return cs_float(math.sin(x.get("value")))


@builtin_func("cos", cs_float)
def cos(x):
    return cs_float(math.cos(x.get("value")))


@builtin_func("tan", cs_float)
def tan(x):
    return cs_float(math.tan(x.get("value")))


#endregion


#region List Functions


@builtin_func("len", cs_int)
def cs_len(x):
    if x.type.subtype(cs_list):
        return len(x.get('value'))
    


@builtin_func("get_at", cs_int)
def cs_get_at(x, index):
    if x.type.subtype(cs_list):
        if index.type.subtype(cs_int):
            return x.get('value')[index.get('value')]



@builtin_func("set_at", cs_int)
def cs_set_at(x, index, obj):
    if x.type.subtype(cs_list):
        if index.type.subtype(cs_int):
            x.get('value')[index.get('value')] = obj.get('value')


#endregion