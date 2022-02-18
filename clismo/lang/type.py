from __future__ import annotations

from typing import Any, Callable, Dict, List


class Type:
    cs_types = {}

    def __init__(self, type_name: str, parent: Type = None):
        self.type_name = type_name
        self.attributes: Dict[str, Any] = {}
        self.parent = parent
        Type.cs_types[type_name] = self

    def add_attribute(self, attribute: str, default: Any = None):
        self.attributes[attribute] = default

    def method(self, method_name: str):
        def method_wrapper(func):
            self.add_attribute(method_name, func)
            return func

        return method_wrapper

    def get_attribute(self, attribute_name: str):
        for attribute in self.attributes:
            if attribute.name == attribute_name:
                return attribute
        return None

    def get_attr_dict(self):
        all_attrs = {}
        if self.parent:
            all_attrs.update(self.parent.get_attr_dict())
        all_attrs.update(self.attributes)
        return all_attrs

    def subtype(self, other: Type):
        if not isinstance(other, tuple):
            other = (other,)
        for subtype in other:
            if self.type_name == subtype.type_name:
                return True
        if self.parent is None:
            return False
        return self.parent.subtype(other)

    def __call__(self, *args, **kwargs):
        return self.attributes["__new__"](*args, **kwargs)

    @staticmethod
    def new(type_name: str, *args, **kwargs):
        if type_name not in Type.cs_types:
            raise ValueError(f"{type_name} is not a valid Clismo type")
        return Type.cs_types[type_name](*args, **kwargs)

    @staticmethod
    def get(type_name: str):
        if type_name not in Type.cs_types:
            raise ValueError(f"{type_name} is not a valid Clismo type")
        return Type.cs_types[type_name]

    @staticmethod
    def get_type(value):
        if isinstance(value, str):
            return Type.get("str")
        if isinstance(value, bool):
            return Type.get("bool")
        if isinstance(value, int):
            return Type.get("int")
        if isinstance(value, float):
            return Type.get("float")
        if value is None:
            return Type.get("none")
        if isinstance(value, list):
            return Type.get("list")
        if isinstance(value, dict):
            return Type.get("dict")
        if isinstance(value, tuple):
            return Type.get("tuple")
        if callable(value):
            return Type.get("function")
        return value

    @staticmethod
    def resolve_type(value):
        val_type = Type.get_type(value)
        return val_type(value)

    def __repr__(self):
        return f"<Type {self.type_name}>"

    def __str__(self):
        return f"<Type {self.type_name}>"


class Instance:
    def __init__(self, _type: Type):
        self.type = _type
        self._dict = self.type.get_attr_dict()
        self._dict["__dict__"] = self._dict

    def get(self, attr_name):
        if attr_name == "__dict__":
            return Type.get("dict")(self._dict)
        if attr_name not in self._dict:
            raise ValueError(f"{self.type.type_name} has no attribute {attr_name}")
        return self._dict[attr_name]

    def set(self, attr_name, value):
        self._dict[attr_name] = value

    def has_value(self):
        return self.type.type_name in ["int", "float", "str", "bool"]

    def get_value(self):
        if self.has_value():
            return self.get("__new__")(self.get("value"))
        return self

    def __iter__(self):
        iterator = self.get("__iter__")(self)
        while True:
            try:
                yield iterator.get("__next__")(iterator)
            except StopIteration:
                break

    def __repr__(self):
        return self.get("__repr__")(self).get("value")


cs_object = Type("object")
cs_float = Type("float", cs_object)
cs_int = Type("int", cs_float)
cs_bool = Type("bool", cs_int)
cs_str = Type("str", cs_object)
cs_list = Type("list", cs_object)
cs_tuple = Type("tuple", cs_object)
cs_none = Type("none", cs_object)
