from clismo.lang.type import Instance, Type

cs_object = Type.get("object")


@cs_object.method("__new__")
def cs__new__(cls, *args, **kwargs):
    inst = Instance(cs_object)
    inst.get("__init__")(inst, *args, **kwargs)
    return inst