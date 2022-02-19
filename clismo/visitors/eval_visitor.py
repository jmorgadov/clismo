import operator
import random

import clismo.builtin as builtin
import clismo.cs_ast as ast
from clismo.lang.type import Type
from clismo.lang.visitor import Visitor
from clismo.optimization.client_server_optimizer import ModelOptimizer
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
    ast.Operator.UADD: lambda x: +x,
    ast.Operator.USUB: lambda x: -x,
    ast.Operator.INVERT: operator.invert,
    ast.Operator.NOT: operator.not_,
}


def get_real_value(obj):
    val = obj.value
    if (
        isinstance(val, list)
        and val
        and not isinstance(val[0], (Client, Server, Step, Simulation))
    ):
        val = [item.value for item in val]
    return val


def get_clismo_type(val):
    if isinstance(val, bool):
        return builtin.cs_bool(val)
    if isinstance(val, int):
        return builtin.cs_int(val)
    if isinstance(val, float):
        return builtin.cs_float(val)
    if isinstance(val, str):
        return builtin.cs_str(val)
    if isinstance(val, list):
        items = [get_clismo_type(item) for item in val]
        if isinstance(items[0], (Client, Server, Step, Simulation)):
            type_ = type(items[0]).__name__.lower()
        else:
            type_ = items[0].type.type_name
        return Type.get(f"{type_}_list")(items)
    if isinstance(val, (Client, Server, Step, Simulation)):
        return val
    raise TypeError(f"Can not convert type {type(val)}")


class EvalVisitor:
    visitor = Visitor().visitor

    def __init__(self, objects):
        self.simulation = None
        self.current_obj = None
        self.current_client = None
        self.objects = objects
        self.objects_by_name = {}
        for obj in self.objects.values():
            self.objects_by_name.update(obj)
        self.context = {}
        self.flags = {
            "return": None,
            "nextloop": False,
            "endloop": False,
        }

    def resolve(self, name):
        if name == "self":
            return self.current_obj
        if name == "time":
            return builtin.cs_float(self.simulation.time)
        if name == "clients":
            return builtin.cs_int(self.simulation.clients)
        if name == "current_client":
            return self.current_client
        if name in self.context:
            return self.context[name]
        if name in self.objects_by_name:
            return self.objects_by_name[name]
        raise Exception(f"Unknown name: {name}")

    @visitor
    def visit(self, node: ast.Program):
        for stmt in node.stmts:
            self.visit(stmt)
        for sim in self.objects["Simulations"].values():
            self.simulation = sim
            mode = sim.attrs.get("mode", "run")
            max_iter = sim.attrs.get("max_iter", 5)
            pop_size = sim.attrs.get("pop_size", 10)
            mut_prob = sim.attrs.get("mut_prob", 0.1)
            best_sel = sim.attrs.get("best_sel", 3)
            new_rand = sim.attrs.get("new_rand", 2)
            logs = sim.attrs.get("logs", False)

            if mode == "run":
                sim.run(logs)
                print("Total time:", sim.time)
                print("Clients attended:", sim.clients)
            else:
                opt = ModelOptimizer(
                    sim,
                    max_iter=max_iter,
                    population_size=pop_size,
                    mutation_prob=mut_prob,
                    best_selection_count=best_sel,
                    generate_new_randoms=new_rand,
                )
                opt.run()

    @visitor
    def visit(self, node: ast.ClientDef):
        self.current_obj = self.objects_by_name[node.name]
        for item in node.body:
            self.visit(item)

    @visitor
    def visit(self, node: ast.ServerDef):
        self.current_obj = self.objects_by_name[node.name]
        for item in node.body:
            self.visit(item)

    @visitor
    def visit(self, node: ast.StepDef):
        self.current_obj = self.objects_by_name[node.name]
        for item in node.body:
            self.visit(item)

    @visitor
    def visit(self, node: ast.SimulationDef):
        self.current_obj = self.objects_by_name[node.name]
        for item in node.body:
            self.visit(item)

    @visitor
    def visit(self, node: ast.Attr):
        obj = self.current_obj
        val = get_real_value(self.visit(node.value))
        if isinstance(obj, Step):
            if node.name == "servers":
                obj.servers = val
            else:
                obj.attrs[node.name] = val
        if isinstance(obj, Simulation):
            if node.name == "time_limit":
                obj.time_limit = val
            if node.name == "client_limit":
                obj.client_limit = val
            if node.name == "steps":
                obj.steps = val
            else:
                obj.attrs[node.name] = val
        else:
            obj.attrs[node.name] = val

    @visitor
    def visit(self, node: ast.Function):
        obj = self.current_obj

        def func():
            self.current_obj = obj
            for stmt in node.body:
                self.visit(stmt)
            val = self.flags.get("return", None)
            self.flags["return"] = None
            return get_real_value(val)

        if node.name == "possible":
            attr_name = node.info[0]
            obj.add_possible_change(func, attr_name)

        if node.name == "on_server_out":
            for server in node.info:
                name = server
                obj.add_on_server_out_callback(func, name)

        if node.name == "attend_client":

            def attend_client(server, client):
                self.current_obj = server
                self.current_client = client
                for stmt in node.body:
                    self.visit(stmt)
                val = self.flags.get("return", None)
                self.flags["return"] = None
                return get_real_value(val)

            self.current_obj.func = attend_client

        if node.name == "arrive":
            for client in node.info:
                obj.add_arrival_func(func, self.objects["Clients"][client])

        if node.name == "minimize":
            obj.minimize_func = func

    @visitor
    def visit(self, node: ast.Assign):
        val = self.visit(node.value)
        self.context[node.name] = val

    @visitor
    def visit(self, node: ast.If):
        cond_val = get_real_value(self.visit(node.cond))
        if cond_val:
            for stmt in node.then:
                self.visit(stmt)
                if (
                    self.flags["endloop"]
                    or self.flags["nextloop"]
                    or self.flags["return"] is not None
                ):
                    break
        elif node.els:
            for stmt in node.els:
                self.visit(stmt)
                if (
                    self.flags["endloop"]
                    or self.flags["nextloop"]
                    or self.flags["return"] is not None
                ):
                    break

    @visitor
    def visit(self, node: ast.Return):
        val = self.visit(node.value)
        self.flags["return"] = val
        return val

    @visitor
    def visit(self, node: ast.Loop):
        start = builtin.cs_int(0) if node.start is None else self.visit(node.start)
        end = builtin.cs_int(-1) if node.end is None else self.visit(node.end)
        step = builtin.cs_int(1) if node.step is None else self.visit(node.step)
        while start.value < end.value:
            if node.target:
                self.context[node.target] = start
            for stmt in node.body:
                self.visit(stmt)
                if self.flags["return"] is not None:
                    break
                if self.flags["nextloop"]:
                    self.flags["nextloop"] = False
                    continue
                if self.flags["endloop"]:
                    self.flags["endloop"] = False
                    break
            start.value += step.value
        if node.target:
            self.context.pop(node.target)

    @visitor
    def visit(self, node: ast.EndLoop):
        self.flags["endloop"] = True

    @visitor
    def visit(self, node: ast.NextLoop):
        self.flags["nextloop"] = True

    @visitor
    def visit(self, node: ast.Call):
        args = [self.visit(arg) for arg in node.args]
        if node.name == "get":
            obj, val = args[0], get_real_value(args[1])
            if not isinstance(obj, (Client, Server, Step, Simulation)):
                raise ValueError(
                    "get() can only be called on clients, servers, steps or simulations"
                )
            if hasattr(obj, val):
                return get_clismo_type(getattr(obj, get_real_value(args[1])))
            if val in obj.attrs:
                return get_clismo_type(obj.attrs[val])
            raise Exception(f"{obj.name} has no attribute {val}")
        if node.name == "set":
            obj, attr, val = args[0], get_real_value(args[1]), get_real_value(args[2])
            if not isinstance(obj, (Client, Server, Step, Simulation)):
                raise ValueError(
                    "set() can only be called on clients, servers, steps or simulations"
                )
            if hasattr(obj, attr):
                setattr(obj, attr, val)
            else:
                obj.attrs[attr] = val
            return builtin.cs_none(None)
        return builtin.resolve(node.name)[0](*args)

    @visitor
    def visit(self, node: ast.BinOp):
        oper = OPERATOR_FUNC[node.op]
        left_val = get_real_value(self.visit(node.left))
        right_val = get_real_value(self.visit(node.right))
        return get_clismo_type(oper(left_val, right_val))

    @visitor
    def visit(self, node: ast.UnaryOp):
        oper = OPERATOR_FUNC[node.op]
        val = self.visit(node.expr)
        return get_clismo_type(oper(get_real_value(val)))

    @visitor
    def visit(self, node: ast.ListExpr):
        elements = [self.visit(item) for item in node.elements]
        if isinstance(elements[0], (Client, Server, Step, Simulation)):
            type_ = type(elements[0]).__name__.lower()
        else:
            type_ = elements[0].type.type_name
        return Type.get(f"{type_}_list")(elements)

    @visitor
    def visit(self, node: ast.Name):
        return self.resolve(node.name)

    @visitor
    def visit(self, node: ast.Constant):
        val = node.value
        if isinstance(val, bool):
            return builtin.cs_bool(val)
        if isinstance(val, int):
            return builtin.cs_int(val)
        if isinstance(val, float):
            return builtin.cs_float(val)
        if isinstance(val, str):
            return builtin.cs_str(val)
