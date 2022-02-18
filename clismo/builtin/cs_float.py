from clismo.lang.type import Instance, Type

cs_float = Type.get("float")


@cs_float.method("__new__")
def cs__new__(value: float):
    _inst = Instance(cs_float)
    _inst.set("value", float(value))
    return _inst
