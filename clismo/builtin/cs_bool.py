from clismo.lang.type import Instance, Type

cs_bool = Type.get("bool")


@cs_bool.method("__new__")
def cs__new__(value: float):
    _inst = Instance(cs_bool)
    _inst.set("value", bool(value))
    return _inst
