from clismo.lang.type import Instance, Type

cs_int = Type.get("int")


@cs_int.method("__new__")
def cs__new__(value: float):
    _inst = Instance(cs_int)
    _inst.set("value", int(value))
    return _inst