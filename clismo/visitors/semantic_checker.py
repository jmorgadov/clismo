import clismo.builtin as builtin
import clismo.cs_ast as ast
from clismo.lang.visitor import Visitor

# from clismo.sim.client import Client
# from clismo.sim.server import Server
# from clismo.sim.simulation import Simulation
# from clismo.sim.step import Step

# pylint: disable=function-redefined
# pylint: disable=missing-function-docstring
# pylint: disable=unpacking-non-sequence


def _get_type(node, context):
    if isinstance(node, ast.Constant):
        val = node.value
        if isinstance(val, bool):
            return builtin.cs_bool
        if isinstance(val, int):
            return builtin.cs_int
        if isinstance(val, float):
            return builtin.cs_float
        if isinstance(val, str):
            return builtin.cs_str
        raise Exception("Unknown type of constant")
    if isinstance(node, ast.ListExpr):
        return builtin.cs_list
    if isinstance(node, ast.Name):
        if node.name not in context:
            raise Exception("Unknown variable: " + node.name)
        return context[node.value]
    raise Exception("Unknown type of node")


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
        }
        self.return_type = None

    def resolve(self, name):
        if name in self.context:
            return self.context[name]
        if name in self.attrs:
            return self.attrs[name]
        if name in self.global_vars:
            return self.global_vars[name]
        raise Exception(f"Unknown variable: {name}")

    def define(self, name, type_):
        if name in self.global_vars:
            raise Exception(f"Can not redefine global variable: {name}")
        self.context[name] = type_

    @visitor
    def visit(self, node: ast.Program):
        for stmt in node.stmts:
            self.visit(stmt)

    def _check_function_body(self, func_name, info, body, attrs):
        for attr_name, attr_val in attrs.items():
            self.attrs[attr_name] = _get_type(attr_val, self.context)
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

    @visitor
    def visit(self, node: ast.ClientDef):
        attrs, functions = self._get_attrs_and_functions(
            self.types["Clients"][node.name]
        )
        if "on_server_out" in functions:
            val = functions.pop("on_server_out")
            for info, body in val.items():
                for server_name in info:
                    if server_name not in self.types["Servers"]:
                        raise TypeError(
                            f"{node.name} on_server_out refers to "
                            f"unknown server {server_name}."
                        )
                self._check_function_body("on_server_out", info, body, attrs)
        if "possible" in functions:
            val = functions.pop("possible")
            for info, body in val.items():
                self._validate_possible_func(info, functions)
                self._check_function_body("possible", info, body, attrs)
        if functions:
            raise TypeError(
                f"{node.name} has unknown functions: {list(functions.keys())}"
            )

    @visitor
    def visit(self, node: ast.ServerDef):
        attrs, functions = self._get_attrs_and_functions(
            self.types["Servers"][node.name]
        )
        all_clients = list(self.types["Clients"].keys())
        if "attend_client" in functions:
            val = functions.pop("attend_client")
            for info, body in val.items():
                for client_name in info:
                    if client_name not in self.types["Clients"]:
                        raise TypeError(
                            f"{node.name} attend_client refers to "
                            f"unknown client {client_name}."
                        )
                    all_clients.remove(client_name)
                if not info:
                    all_clients = ["DefaultClient"]
                self._check_function_body("attend_client", info, body, attrs)
        if "possible" in functions:
            val = functions.pop("possible")
            for info, body in val.items():
                self._validate_possible_func(info, functions)
                self._check_function_body("possible", info, body, attrs)
        if len(all_clients) > 1 or (
            len(all_clients) == 1 and all_clients[0] != "DefaultClient"
        ):
            raise TypeError(
                f"Server {node.name} does not attend the following "
                f"clients: {all_clients}."
            )
        if functions:
            raise TypeError(
                f"{node.name} has unknown functions: {list(functions.keys())}"
            )

    @visitor
    def visit(self, node: ast.StepDef):
        attrs, functions = self._get_attrs_and_functions(self.types["Steps"][node.name])
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
                self._check_function_body("possible", info, body, attrs)
        if functions:
            raise TypeError(
                f"{node.name} has unknown functions: {list(functions.keys())}"
            )

    @visitor
    def visit(self, node: ast.SimulationDef):
        attrs, functions = self._get_attrs_and_functions(
            self.types["Simulations"][node.name]
        )

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
            self._check_function_body("arrive", info, body, attrs)

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
                self._check_function_body("minimize", info, body, attrs)

        if "possible" in functions:
            val = functions.pop("possible")
            for info, body in val.items():
                self._validate_possible_func(info, functions)
                self._check_function_body("possible", info, body, attrs)
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
        if old_type != val_type:
            raise TypeError(
                f"{node.name} has type {old_type.type_name} but is being assigned "
                f"type {val_type.type_name}."
            )

    @visitor
    def visit(self, node: ast.If):
        cond_type = self.visit(node.cond)
        if cond_type != builtin.cs_bool:
            raise TypeError(
                f"Condtion has type {cond_type.type_name} but must be bool."
            )
        for stmt in node.then:
            self.visit(stmt)

    @visitor
    def visit(self, node: ast.Return):
        val_type = self.visit(node.value)
        if val_type != self.return_type:
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
            if start_type != builtin.cs_int:
                raise TypeError(
                    f"Loop start has type {start_type.type_name} but must be int."
                )
        if end is not None:
            end_type = self.visit(end)
            if end_type != builtin.cs_int:
                raise TypeError(
                    f"Loop end has type {end_type.type_name} but must be int."
                )
        if step is not None:
            step_type = self.visit(step)
            if step_type != builtin.cs_int:
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
        for arg in node.args:
            self.visit(arg)
        return builtin.resolve(node.name)[1]

    @visitor
    def visit(self, node: ast.BinOp):
        pass

    @visitor
    def visit(self, node: ast.UnaryOp):
        return self.visit(node.value)

    @visitor
    def visit(self, node: ast.ListExpr):
        for item in node.elements:
            self.visit(item)
        return builtin.cs_list

    @visitor
    def visit(self, node: ast.Name):
        return self.resolve(node.name)

    @visitor
    def visit(self, node: ast.Constant):
        return _get_type(node.value, None)
