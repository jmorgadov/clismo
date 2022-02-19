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
        if self.type_name == "any":
            return True
        if not isinstance(other, tuple):
            other = (other,)
        for subtype in other:
            if self.type_name == subtype.type_name:
                return True
        if self.parent is None:
            return False
        return self.parent.subtype(other)

    def __call__(self, value):
        return Instance(self, value)

    @staticmethod
    def new(type_name: str, *args, **kwargs):
        if type_name not in Type.cs_types:
            raise ValueError(f"{type_name} is not a valid Clismo type")
        return Type.cs_types[type_name](*args, **kwargs)

    @staticmethod
    def get(type_name: str):
        if type_name == "list":
            return (
                cs_list_of_float,
                cs_list_of_int,
                cs_list_of_str,
                cs_list_of_bool,
                cs_list_of_client,
                cs_list_of_server,
                cs_list_of_step,
                cs_list_of_simulation,
            )
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
    def __init__(self, _type: Type, value):
        self.type = _type
        self.value = value


cs_object = Type("object")
cs_float = Type("float", cs_object)
cs_int = Type("int", cs_float)
cs_bool = Type("bool", cs_int)
cs_str = Type("str", cs_object)
cs_none = Type("none", cs_object)
cs_any = Type("any", cs_object)
cs_client = Type("client", cs_object)
cs_server = Type("server", cs_object)
cs_step = Type("step", cs_object)
cs_simulation = Type("simulation", cs_object)

cs_list_of_float = Type("float_list", cs_object)
cs_list_of_int = Type("int_list", cs_object)
cs_list_of_str = Type("str_list", cs_object)
cs_list_of_bool = Type("bool_list", cs_object)
cs_list_of_client = Type("client_list", cs_object)
cs_list_of_server = Type("server_list", cs_object)
cs_list_of_step = Type("step_list", cs_object)
cs_list_of_simulation = Type("simulation_list", cs_object)
