from clismo.lang.type import Instance, Type

cs_str = Type.get("str")
cs_list = Type.get("list")


@cs_list.method("__new__")
def cs__new__(value: list):
    _inst = Instance(cs_list)
    _inst.set("value", list(value))
    return _inst


@cs_list.method("__repr__")
def cs__repr__(self):
    return cs_str(repr(self.get("value")))