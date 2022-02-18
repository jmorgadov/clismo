from clismo.lang.type import Instance, Type

cs_str = Type.get("str")


@cs_str.method("__new__")
def cs__new__(value: str):
    _inst = Instance(cs_str)
    _inst.set("value", str(value))
    return _inst


@cs_str.method("__repr__")
def cs__repr__(self):
    return cs_str(f'\'{self.get("value")}\'')