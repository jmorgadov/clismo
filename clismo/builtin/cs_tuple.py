import clismo.exceptions as excpt
from clismo.lang.type import Instance, Type

cs_tuple = Type.get("tuple")
cs_str = Type.get("str")


@cs_tuple.method("__new__")
def cs__new__(value: set):
    _inst = Instance(cs_tuple)
    _inst.set("value", tuple(value))
    return _inst


@cs_tuple.method("__repr__")
def cs__repr__(self):
    return cs_str(repr(self.get("value")))