import builtins
import math
import random
from time import sleep

import clismo.exceptions as excpt
from clismo.lang.type import Instance, Type

__BUILTINS = {}

cs_float = Type.get("float")
cs_int = Type.get("int")
cs_str = Type.get("str")
cs_bool = Type.get("bool")
cs_none = Type.get("none")
cs_list = Type.get("list")


def builtin_func(func_name, return_type):
    def deco(func):
        __BUILTINS[func_name] = (func, return_type)
        return func

    return deco


def resolve(func_name):
    return __BUILTINS.get(func_name, None)


# region Numeric Functions


@builtin_func("abs", cs_float)
def cs_abs(x: cs_float):
    if x.type.subtype(cs_float):
        return cs_float(builtins.abs(x.value))
    raise TypeError("abs() argument must be a float")


@builtin_func("bin", cs_str)
def cs_bin(x: cs_int):
    if x.type.subtype(cs_int):
        return cs_str(builtins.bin(x.value))
    raise TypeError("bin() argument must be an int")


@builtin_func("round", cs_float)
def cs_round(x, ndigits=None):
    if x.type.subtype(cs_float):
        if ndigits is None:
            return cs_float(builtins.round(x.value))
        if ndigits.type.subtype(cs_int):
            return cs_float(builtins.round(x.value, ndigits.value))
        raise TypeError("round() second argument must be an int")
    raise TypeError("round() argument must be a float")


@builtin_func("rand", cs_float)
def cs_rand():
    return cs_float(random.random())


@builtin_func("randint", cs_int)
def cs_randint(a, b):
    if a.type.subtype(cs_int) and b.type.subtype(cs_int):
        return cs_int(random.randint(a.value, b.value))
    raise TypeError("randint() arguments must be int")


@builtin_func("norm", cs_float)
def cs_norm():
    return cs_float(random.normalvariate(0, 1))


@builtin_func("sqrt", cs_float)
def cs_sqrt(x):
    if x.type.subtype(cs_float):
        return cs_float(math.sqrt(x.value))
    raise TypeError("sqrt() argument must be a float")


@builtin_func("log", cs_float)
def log(x, base):
    if x.type.subtype(cs_float):
        if base.type.subtype(cs_int):
            return cs_float(math.log(x.value, base.value))
        raise TypeError("log() second argument must be an int")
    raise TypeError("log() argument must be a float")


@builtin_func("log2", cs_float)
def log2(x):
    if x.type.subtype(cs_float):
        return cs_float(math.log2(x.value))
    raise TypeError("log2() argument must be a float")


@builtin_func("exp", cs_float)
def exp(x):
    if x.type.subtype(cs_float):
        return cs_float(math.exp(x.value))
    raise TypeError("exp() argument must be a float")


@builtin_func("ceil", cs_int)
def ceil(x):
    if x.type.subtype(cs_int):
        return cs_int(math.ceil(x.value))
    raise TypeError("ceil() argument must be an int")


@builtin_func("floor", cs_int)
def floor(x):
    if x.type.subtype(cs_int):
        return cs_int(math.floor(x.value))
    raise TypeError("floor() argument must be an int")


@builtin_func("sin", cs_float)
def sin(x):
    if x.type.subtype(cs_float):
        return cs_float(math.sin(x.value))
    raise TypeError("sin() argument must be a float")


@builtin_func("cos", cs_float)
def cos(x):
    if x.type.subtype(cs_float):
        return cs_float(math.cos(x.value))
    raise TypeError("cos() argument must be a float")


@builtin_func("tan", cs_float)
def tan(x):
    if x.type.subtype(cs_float):
        return cs_float(math.tan(x.value))
    raise TypeError("tan() argument must be a float")


# endregion


# region List Functions


@builtin_func("len", cs_int)
def cs_len(x):
    if x.type.subtype(cs_list):
        return cs_int(len(x.value))
    raise TypeError("len() argument must be a list")


@builtin_func("get_at", lambda x, i: Type.get(x.type_name[:-5]))
def cs_get_at(x, index):
    if x.type.subtype(cs_list):
        if index.type.subtype(cs_int):
            return x.value[index.value]
        raise TypeError("get_at() second argument must be an int")
    raise TypeError("get_at() argument must be a list")


@builtin_func("set_at", cs_none)
def cs_set_at(x, index, obj):
    if x.type.subtype(cs_list):
        if index.type.subtype(cs_int):
            x.value[index.value] = obj
            return cs_none()
        raise TypeError("set_at() second argument must be an int")
    raise TypeError("set_at() argument must be a list")


@builtin_func("append", lambda x, o: x)
def cs_append(x, obj):
    if x.type.subtype(cs_list):
        x.value.append(obj)
        return x
    raise TypeError("append() argument must be a list")


@builtin_func("list", lambda x: Type.get(f"{x}_list"))
def cs_new_list(type_):
    list_type = Type.get(f"{type_.value}_list")
    return Instance(list_type, [])


# endregion


# region String Functions


@builtin_func("startswith", cs_bool)
def cs_startswith(x, y):
    if x.type.subtype(cs_str) and y.type.subtype(cs_str):
        return x.value.startswith(y.value)
    raise TypeError("startswith() arguments must be strings")


@builtin_func("isdigit", cs_bool)
def cs_isdigit(x):
    if x.type.subtype(cs_str):
        return x.value.isdigit(x.value)
    raise TypeError("isdigit() argument must be a str")


@builtin_func("lower", cs_str)
def cs_lower(x):
    if x.type.subtype(cs_str):
        return x.value.lower(x.value)
    raise TypeError("lower() argument must be a str")


@builtin_func("capitalize", cs_str)
def cs_capitalize(x):
    if x.type.subtype(cs_str):
        return x.value.capitalize(x.value)
    raise TypeError("capitalize() argument must be a str")


# endregion
