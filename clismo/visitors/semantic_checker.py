import operator

import clismo.builtin as builtin
import clismo.cs_ast as ast
from clismo.lang.type import Type
from clismo.lang.visitor import Visitor
from clismo.sim.client import Client
from clismo.sim.server import Server
from clismo.sim.simulation import Simulation
from clismo.sim.step import Step

# pylint: disable=function-redefined
# pylint: disable=missing-function-docstring
# pylint: disable=unpacking-non-sequence


OPERATOR_FUNC = {
    ast.Operator.ADD: operator.add,
    ast.Operator.SUB: operator.sub,
    ast.Operator.MUL: operator.mul,
    ast.Operator.DIV: operator.truediv,
    ast.Operator.POW: operator.pow,
    ast.Operator.MOD: operator.mod,
    ast.Operator.POW: operator.pow,
    ast.Operator.LSHIFT: operator.lshift,
    ast.Operator.RSHIFT: operator.rshift,
    ast.Operator.BIT_XOR: operator.xor,
    ast.Operator.BIT_AND: operator.and_,
    ast.Operator.BIT_OR: operator.or_,
    ast.Operator.FLOORDIV: operator.floordiv,
    ast.Operator.EQ: operator.eq,
    ast.Operator.NOT_EQ: operator.ne,
    ast.Operator.LT: operator.lt,
    ast.Operator.GT: operator.gt,
    ast.Operator.LTE: operator.le,
    ast.Operator.GTE: operator.ge,
}


def _get_type_example(type_):
    if type_ == builtin.cs_bool:
        return True
    if type_ == builtin.cs_int:
        return 1
    if type_ == builtin.cs_float:
        return 1.0
    if type_ == builtin.cs_str:
        return "str"
    if type_.type_name.startswith("cs_list"):
        return [1, 2, 3]
    if type_ == builtin.cs_client:
        return Client("test")
    if type_ == builtin.cs_server:
        return Server("test", lambda x: 1)
    if type_ == builtin.cs_simulation:
        return Simulation("test", [], time_limit=1)
    if type_ == builtin.cs_step:
        return Step("test")
    raise Exception(f"Unknown type of node {type_}")


def _get_built_in_type(val):
    if isinstance(val, bool):
        return builtin.cs_bool
    if isinstance(val, int):
        return builtin.cs_int
    if isinstance(val, float):
        return builtin.cs_float
    if isinstance(val, str):
        return builtin.cs_str
    raise Exception(f"Unknown type of constant {val}")


class SemanticChecker:
    visitor = Visitor().visitor

    def __init__(self, types):
        self.types = types
        self.context = {}
        self.attrs = {}
        self.global_vars = {
            "time": builtin.cs_float,
            "clients": builtin.cs_int,
            "self": builtin.cs_object,
            "current_client": builtin.cs_client,
        }
        self.return_type = None
        self.current_func_name = None
        self.objects = {
            "Clients": {"DefaultClient": Client("DefaultClient")},
            "Servers": {},
            "Steps": {},
            "Simulations": {},
        }

    def resolve(self, name):
        if name in self.context:
            return self.context[name]
        if name in self.attrs:
            return self.attrs[name]
        if name in self.global_vars:
            return self.global_vars[name]
        if name in self.types["Clients"]:
            return builtin.cs_client
        if name in self.types["Servers"]:
            return builtin.cs_server
        if name in self.types["Simulations"]:
            return builtin.cs_simulation
        if name in self.types["Steps"]:
            return builtin.cs_step
        raise Exception(f"Unknown variable: {name}")

    def define(self, name, type_):
        if name in self.global_vars:
            raise Exception(f"Can not redefine global variable: {name}")
        self.context[name] = type_

    def _get_list_type(self, node):
        first_type = self.visit(node.elements[0])
        for elem in node.elements[1:]:
            if self.visit(elem) != first_type:
                raise Exception("All elements of list must be of the same type")
        list_type = f"{first_type.type_name}_list"
        return Type.get(list_type)

    def _get_type(self, node):
        if isinstance(node, ast.Constant):
            val = node.value
            return _get_built_in_type(val)
        if isinstance(node, ast.ListExpr):
            return self._get_list_type(node)
        if isinstance(node, ast.Name):
            if node.name not in self.context:
                raise Exception("Unknown variable: " + node.name)
            return self.context[node.value]
        raise Exception(f"Unknown type of node {node}")

    @visitor
    def visit(self, node: ast.Program):
        for stmt in node.stmts:
            self.visit(stmt)
        if not self.objects["Simulations"]:
            raise Exception("There must exist at least one simulation object")

    def _check_function_body(self, func_name, info, body, attrs, obj):
        if obj == "Clients":
            obj_type = builtin.cs_client
        elif obj == "Servers":
            obj_type = builtin.cs_server
        elif obj == "Simulations":
            obj_type = builtin.cs_simulation
        elif obj == "Steps":
            obj_type = builtin.cs_step
        else:
            raise Exception(f"Unknown object type: {obj}")

        self.global_vars["self"] = obj_type
        self.current_func_name = func_name
        for attr_name, attr_val in attrs.items():
            self.attrs[attr_name] = self._get_type(attr_val)
        if func_name == "on_server_out":
            self.return_type = builtin.cs_none
        elif func_name == "attend_client":
            self.return_type = builtin.cs_float
        elif func_name == "arrive":
            self.return_type = builtin.cs_float
        elif func_name == "minimize":
            self.return_type = builtin.cs_float
        elif func_name == "possible":
            self.return_type = self.resolve(info[0])
        else:
            assert False, "Unreachable"
        for stmt in body:
            self.visit(stmt)

    def _get_attrs_and_functions(self, dict_):
        functions = {k: v for k, v in dict_.items() if isinstance(v, dict)}
        attrs = {k: v for k, v in dict_.items() if k not in functions}
        if any(k in attrs for k in self.global_vars):
            raise Exception("Can not redefine global variable as an attribute")
        return attrs, functions

    def _validate_possible_func(self, info, attrs):
        if len(info) == 0:
            raise Exception("No attribute specified on 'possible' function")
        if len(info) > 1:
            raise Exception("Too many attributes specified on 'possible' function")
        if info[0] not in attrs:
            raise Exception(
                f"Attribute '{info[0]}' (specified on 'possible' "
                f"function) does not exist"
            )

    def _set_attrs_type(self, attrs, type_, name):
        for attr_name, attr_val in attrs.items():
            attr_type = self.visit(attr_val)
            self.types[type_][name][attr_name] = attr_type

    @visitor
    def visit(self, node: ast.ClientDef):
        attrs, functions = self._get_attrs_and_functions(
            self.types["Clients"][node.name]
        )
        self._set_attrs_type(attrs, "Clients", node.name)
        self.objects["Clients"][node.name] = Client(node.name)
        if "on_server_out" in functions:
            val = functions.pop("on_server_out")
            for info, body in val.items():
                for server_name in info:
                    if server_name not in self.types["Servers"]:
                        raise TypeError(
                            f"{node.name} on_server_out refers to "
                            f"unknown server {server_name}."
                        )
                self._check_function_body("on_server_out", info, body, attrs, "Clients")
        if "possible" in functions:
            val = functions.pop("possible")
            for info, body in val.items():
                self._validate_possible_func(info, attrs)
                self._check_function_body("possible", info, body, attrs, "Clients")
        if functions:
            raise TypeError(
                f"{node.name} has unknown functions: {list(functions.keys())}"
            )

    @visitor
    def visit(self, node: ast.ServerDef):
        attrs, functions = self._get_attrs_and_functions(
            self.types["Servers"][node.name]
        )
        self._set_attrs_type(attrs, "Servers", node.name)
        self.objects["Servers"][node.name] = Server(node.name, None)
        if "attend_client" in functions:
            val = functions.pop("attend_client")
            if len(list(val.items())) != 1:
                raise TypeError("There must exist exactly one 'attend_client' function")
            for info, body in val.items():
                if info:
                    raise TypeError(
                        "'attend_client' function must not have any specifications"
                    )
                self._check_function_body("attend_client", [], body, attrs, "Servers")
        if "possible" in functions:
            val = functions.pop("possible")
            for info, body in val.items():
                self._validate_possible_func(info, attrs)
                self._check_function_body("possible", info, body, attrs, "Servers")
        if functions:
            raise TypeError(
                f"{node.name} has unknown functions: {list(functions.keys())}"
            )

    @visitor
    def visit(self, node: ast.StepDef):
        attrs, functions = self._get_attrs_and_functions(self.types["Steps"][node.name])
        self._set_attrs_type(attrs, "Steps", node.name)
        self.objects["Steps"][node.name] = Step(node.name)
        if "servers" not in attrs:
            raise TypeError(f"{node.name} does not have servers.")
        servers = attrs["servers"]
        if not isinstance(servers, ast.ListExpr):
            raise TypeError(f"{node.name} servers attribute must be a list.")
        for server in servers.elements:
            if not isinstance(server, ast.Name):
                raise TypeError(
                    f"{node.name} servers attribute must be a list of names."
                )
            if server.name not in self.types["Servers"]:
                raise TypeError(
                    f"{node.name} servers attribute refers to "
                    f"unknown server {server.name}."
                )
        if "possible" in functions:
            val = functions.pop("possible")
            for info, body in val.items():
                self._validate_possible_func(info, attrs)
                self._check_function_body("possible", info, body, attrs, "Steps")
        if functions:
            raise TypeError(
                f"{node.name} has unknown functions: {list(functions.keys())}"
            )

    @visitor
    def visit(self, node: ast.SimulationDef):
        attrs, functions = self._get_attrs_and_functions(
            self.types["Simulations"][node.name]
        )
        self._set_attrs_type(attrs, "Simulations", node.name)
        self.objects["Simulations"][node.name] = Simulation(node.name, None)

        # Check steps
        if "steps" not in attrs:
            raise TypeError(f"{node.name} does not have steps.")
        steps = attrs["steps"]
        if not isinstance(steps, ast.ListExpr):
            raise TypeError(f"{node.name} steps attribute must be a list.")
        for step in steps.elements:
            if not isinstance(step, ast.Name):
                raise TypeError(f"{node.name} steps attribute must be a list of names.")
            if step.name not in self.types["Steps"]:
                raise TypeError(
                    f"{node.name} steps attribute refers to "
                    f"unknown step {step.name}."
                )

        # Check mode
        if "mode" in attrs:
            mode = attrs["mode"]
            if not isinstance(mode, ast.Constant) and not isinstance(mode.value, str):
                raise TypeError(f"{node.name} mode attribute must be a string.")
            mode_val = mode.value
            if mode_val not in ["run", "optimize"]:
                raise TypeError(
                    f"{node.name} mode attribute must be 'run' or 'optimize'."
                )
            if mode_val == "optimize" and not "minimize" in functions:
                raise TypeError(
                    f"{node.name} mode is 'optimize' but does not have "
                    f"a minimize function."
                )

        # Check terminate condition
        if "time_limit" not in attrs and "client_limit" not in attrs:
            raise TypeError(
                f"{node.name} does not have a time_limit or client_limit attribute."
            )
        if "time_limit" in attrs:
            val = attrs["time_limit"]
            if not isinstance(val, ast.Constant) and not isinstance(val.value, float):
                raise TypeError(f"{node.name} time_limit attribute must be float.")
        if "client_limit" in attrs:
            val = attrs["client_limit"]
            if not isinstance(val, ast.Constant) and not isinstance(val.value, int):
                raise TypeError(f"{node.name} client_limit attribute must be int.")

        # Check arrive function
        if "arrive" not in functions:
            raise TypeError(f"{node.name} does not have an arrive function.")
        arrive_overloads = functions.pop("arrive")
        for info, body in arrive_overloads.items():
            if not info:
                raise TypeError(
                    f"{node.name} arrive function must specify at least one "
                    "client type."
                )
            for client_type in info:
                if client_type not in self.types["Clients"]:
                    raise TypeError(
                        f"{node.name} arrive function refers to "
                        f"unknown client type {client_type}."
                    )
            self._check_function_body("arrive", info, body, attrs, "Simulations")

        # Check minimize function
        if "minimize" in functions:
            val = functions.pop("minimize")
            if len(list(val.keys())) > 1:
                raise TypeError(f"{node.name} minimize function has too many overloads")
            for info, body in val.items():
                if info:
                    raise TypeError(
                        f"{node.name} minimize function must have no specifications"
                    )
                self._check_function_body("minimize", info, body, attrs, "Simulations")

        if "possible" in functions:
            val = functions.pop("possible")
            for info, body in val.items():
                self._validate_possible_func(info, attrs)
                self._check_function_body("possible", info, body, attrs, "Simulations")
        if functions:
            raise TypeError(
                f"{node.name} has unknown functions: {list(functions.keys())}"
            )

    @visitor
    def visit(self, node: ast.Attr):
        pass

    @visitor
    def visit(self, node: ast.Function):
        pass

    @visitor
    def visit(self, node: ast.Assign):
        val_type = self.visit(node.value)
        if node.decl:
            self.define(node.name, val_type)
            return
        old_type = self.resolve(node.name)
        if not old_type.subtype(val_type):
            raise TypeError(
                f"{node.name} has type {old_type.type_name} but is being assigned "
                f"type {val_type.type_name}."
            )

    @visitor
    def visit(self, node: ast.If):
        cond_type = self.visit(node.cond)
        if not cond_type.subtype(builtin.cs_bool):
            raise TypeError(
                f"Condtion has type {cond_type.type_name} but must be bool."
            )
        for stmt in node.then:
            self.visit(stmt)

    @visitor
    def visit(self, node: ast.Return):
        val_type = self.visit(node.value)
        if not val_type.subtype(self.return_type):
            raise TypeError(
                f"Return value has type {val_type.type_name} but must "
                f"be {self.return_type.type_name}."
            )

    @visitor
    def visit(self, node: ast.Loop):
        if node.target is not None:
            self.define(node.target, builtin.cs_int)
        start, end, step = node.start, node.end, node.step
        if start is not None:
            start_type = self.visit(start)
            if not start_type.subtype(builtin.cs_int):
                raise TypeError(
                    f"Loop start has type {start_type.type_name} but must be int."
                )
        if end is not None:
            end_type = self.visit(end)
            if not end_type.subtype(builtin.cs_int):
                raise TypeError(
                    f"Loop end has type {end_type.type_name} but must be int."
                )
        if step is not None:
            step_type = self.visit(step)
            if not step_type.subtype(builtin.cs_int):
                raise TypeError(
                    f"Loop step has type {step_type.type_name} but must be int."
                )
        for stmt in node.body:
            self.visit(stmt)

    @visitor
    def visit(self, node: ast.EndLoop):
        pass

    @visitor
    def visit(self, node: ast.NextLoop):
        pass

    @visitor
    def visit(self, node: ast.Call):
        args_type = [self.visit(arg) for arg in node.args]
        if node.name == "get":
            if len(node.args) != 2:
                raise TypeError(
                    f"get function must have exactly two arguments, "
                    f"but got {len(node.args)}"
                )
            if not isinstance(node.args[1], ast.Name):
                raise TypeError(
                    "get function second argument must be an attribute name"
                )
            obj_type = self.visit(node.args[0])
            if obj_type == builtin.cs_server:
                type_ = "Servers"
            elif obj_type == builtin.cs_simulation:
                type_ = "Simulations"
            elif obj_type == builtin.cs_client:
                type_ = "Clients"
            elif obj_type == builtin.cs_step:
                type_ = "Steps"
            else:
                raise TypeError(
                    f"get function first argument must be a server, "
                    f"simulation, client, or step, but got {obj_type}"
                )
            attr_name = node.args[1].name
            for val in self.types[type_].values():
                if attr_name in val:
                    return val[attr_name]
            raise TypeError(
                f"{type_} {attr_name} does not exist."
            )
        if node.name == "set":
            if len(node.args) != 3:
                raise TypeError(
                    f"set function must have exactly three arguments, "
                    f"but got {len(node.args)}"
                )
            obj_type = self.visit(node.args[0])
            if obj_type == builtin.cs_server:
                type_ = "Servers"
            elif obj_type == builtin.cs_simulation:
                type_ = "Simulations"
            elif obj_type == builtin.cs_client:
                type_ = "Clients"
            elif obj_type == builtin.cs_step:
                type_ = "Steps"
            else:
                raise TypeError(
                    f"get function first argument must be a server, "
                    f"simulation, client, or step, but got {obj_type}"
                )
            if not isinstance(node.args[1], ast.Name):
                raise TypeError(
                    "set function second argument must be an attribute name"
                )
            attr_name = node.args[1].name
            for val in self.types[type_].values():
                if attr_name in val:
                    break
            else:
                raise TypeError(
                    f"{type_} {attr_name} does not exist."
                )
            self.visit(node.args[2])
            return builtin.cs_none
        ret_type = builtin.resolve(node.name)
        if ret_type is None:
            raise TypeError(f"{node.name} is not a known function.")
        if isinstance(ret_type[1], Type):
            return ret_type[1]
        if node.name == "list":
            if len(node.args) != 1:
                raise TypeError(
                    f"list function must have exactly one argument, "
                    f"but got {len(node.args)}"
                )
            if not isinstance(node.args[0], ast.Constant) and not isinstance(
                node.args[0].value, str
            ):
                raise TypeError(f"list function argument must be a constant string")
            return ret_type[1](node.args[0].value)
        return ret_type[1](*args_type)

    @visitor
    def visit(self, node: ast.BinOp):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        oper = OPERATOR_FUNC[node.op]
        exmp_left = _get_type_example(left_type)
        exmp_right = _get_type_example(right_type)
        try:
            new_type = _get_built_in_type(oper(exmp_left, exmp_right))
        except Exception:
            raise TypeError(
                f"{node.op} cannot be applied to types {left_type.type_name} and "
                f"{right_type.type_name}."
            )
        return new_type

    @visitor
    def visit(self, node: ast.UnaryOp):
        return self.visit(node.expr)

    @visitor
    def visit(self, node: ast.ListExpr):
        return self._get_list_type(node)

    @visitor
    def visit(self, node: ast.Name):
        return self.resolve(node.name)

    @visitor
    def visit(self, node: ast.Constant):
        return _get_built_in_type(node.value)
