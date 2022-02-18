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
    if x.type.subtype(cs_float):
        return cs_float(builtins.abs(x.get("value")))
    #raise


@builtin_func("bin", cs_str)
def cs_bin(x: cs_int):
    if x.type.subtype(cs_int):
        return cs_str(builtins.bin(x.get("value")))
    #raise


@builtin_func("round", cs_float)
def cs_round(x, ndigits=None):
    if x.type.subtype(cs_float):
        if ndigits is None:
            return cs_float(builtins.round(x.get("value")))
        if ndigits.type.subtype(cs_int):
            return cs_float(builtins.round(x.get("value"), ndigits.get("value")))
        #raise
    #raise


@builtin_func("rand", cs_float)
def cs_rand():
    return cs_float(random.random())


@builtin_func("randint", cs_str)
def cs_randint(a, b):
    if a.type.subtype(cs_float) and b.type.subtype(cs_int):
        return cs_int(random.randint(a.get("value"), b.get("value")))
    #raise


@builtin_func("norm", cs_float)
def cs_norm():
    return cs_float(random.normalvariate(0, 1))


@builtin_func("sqrt", cs_float)
def cs_sqrt(x):
    if x.type.subtype(cs_float):
        return cs_float(math.sqrt(x.get("value")))
    #raise


@builtin_func("sleep", cs_float)
def cs_sleep(x: cs_float):
    if x.type.subtype(cs_float):
        return cs_float(sleep(x))
    #raise


@builtin_func("log", cs_float)
def log(x, base):
    if x.type.subtype(cs_float):
        if base.type.subtype(cs_int):
            return cs_float(math.log(x.get("value"), base.get("value")))
        #raise
    #raise


@builtin_func("log2", cs_float)
def log2(x):
    if x.type.subtype(cs_float):
        return cs_float(math.log2(x.get("value")))
    #raise


@builtin_func("exp", cs_float)
def exp(x):
    if x.type.subtype(cs_float):
        return cs_float(math.exp(x.get("value")))
    #raise


@builtin_func("ceil", cs_int)
def ceil(x):
    if x.type.subtype(cs_int):
        return cs_int(math.ceil(x.get("value")))
    #raise


@builtin_func("floor", cs_int)
def floor(x):
    if x.type.subtype(cs_int):
        return cs_int(math.floor(x.get("value")))
    #raise


@builtin_func("sin", cs_float)
def sin(x):
    if x.type.subtype(cs_float):
        return cs_float(math.sin(x.get("value")))
    #raise


@builtin_func("cos", cs_float)
def cos(x):
    if x.type.subtype(cs_float):
        return cs_float(math.cos(x.get("value")))
    #raise


@builtin_func("tan", cs_float)
def tan(x):
    if x.type.subtype(cs_float):
        return cs_float(math.tan(x.get("value")))
    #raise


#endregion


#region List Functions


@builtin_func("len", cs_int)
def cs_len(x):
    if x.type.subtype(cs_list):
        return len(x.get('value'))
    #raise
    


@builtin_func("get_at", cs_int)
def cs_get_at(x, index):
    if x.type.subtype(cs_list):
        if index.type.subtype(cs_int):
            return x.get('value')[index.get('value')]
        #raise
    #raise



@builtin_func("set_at", cs_int)
def cs_set_at(x, index, obj):
    if x.type.subtype(cs_list):
        if index.type.subtype(cs_int):
            x.get('value')[index.get('value')] = obj.get('value')
        #raise
    #raise


#endregion