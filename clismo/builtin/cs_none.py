from clismo.lang.type import Instance, Type

cs_bool = Type.get("bool")
cs_none = Type.get("none")


@cs_none.method("__new__")
def cs__new__():
    _inst = Instance(cs_none)
    return _inst


@cs_none.method("__bool__")
def cs__bool__(self: Instance):
    return cs_bool(False)
