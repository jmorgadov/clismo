import clismo.cs_ast as ast
from clismo.lang.visitor import Visitor

# pylint: disable=function-redefined
# pylint: disable=missing-function-docstring
# pylint: disable=unpacking-non-sequence


class TypeBuilder:
    visitor = Visitor().visitor

    def __init__(self):
        self.types = {
            "Clients": {
                "DefaultClient": {},
            },
            "Servers": {},
            "Steps": {},
            "Simulations": {},
        }

    @visitor
    def visit(self, node: ast.Program):
        for stmt in node.stmts:
            self.visit(stmt)

    def _add_type(self, type_, name, attrs):
        self.types[type_][name] = {}
        for attr in attrs:
            key, val = self.visit(attr)
            if isinstance(val, tuple):
                overloads = self.types[type_][name].get(key, {})
                overloads[val[0]] = val[1]
                self.types[type_][name][key] = overloads
            else:
                self.types[type_][name][key] = val

    @visitor
    def visit(self, node: ast.ClientDef):
        self._add_type("Clients", node.name, node.body)

    @visitor
    def visit(self, node: ast.ServerDef):
        self._add_type("Servers", node.name, node.body)

    @visitor
    def visit(self, node: ast.StepDef):
        self._add_type("Steps", node.name, node.body)

    @visitor
    def visit(self, node: ast.SimulationDef):
        self._add_type("Simulations", node.name, node.body)

    @visitor
    def visit(self, node: ast.Attr):
        return node.name, node.value

    @visitor
    def visit(self, node: ast.Function):
        return node.name, (tuple(node.info), node.body)
