from __future__ import annotations

from typing import Any, List

from clismo.compiler.generic_ast import AST


class Program(AST):
    def __init__(self, stmts: List[ObjDef]):
        self.stmts = stmts


class ObjDef(AST):
    def __init__(
        self, obj_type: str, name: str, attrs: List[Attr], functions: List[Function]
    ):
        self.obj_type = obj_type
        self.name = name
        self.attrs = attrs
        self.functions = functions


class ClientDef(ObjDef):
    def __init__(self, name, attrs, functions):
        super().__init__("client", name, attrs, functions)


class ServerDef(ObjDef):
    def __init__(self, name, attrs, functions):
        super().__init__("server", name, attrs, functions)


class StepDef(ObjDef):
    def __init__(self, name, attrs, functions):
        super().__init__("step", name, attrs, functions)


class SimulationDef(ObjDef):
    def __init__(self, name, attrs, functions):
        super().__init__("simulation", name, attrs, functions)


class Attr(AST):
    def __init__(self, name: str, value: Expr):
        self.name = name
        self.value = value


class Function(AST):
    def __init__(self, name: str, info: List[Name], body: List[Stmt]):
        self.name = name
        self.info = info
        self.body = body


class Stmt(AST):
    pass


class Assign(Stmt):
    def __init__(self, name: str, value: Expr):
        self.name = name
        self.value = value


class If(Stmt):
    def __init__(self, cond: Expr, then: List[Stmt], els=None):
        self.cond = cond
        self.then = then
        self.els = els or []


class Return(Stmt):
    def __init__(self, value: Expr):
        self.value = value


class Loop(Stmt):
    def __init__(
        self,
        target: str,
        body: List[Stmt],
        start: Expr = None,
        end: Expr = None,
        step: Expr = None,
    ):
        self.target = target
        self.body = body
        self.start = start
        self.end = end
        self.step = step


class Expr(AST):
    pass


class Call(Expr):
    def __init__(self, name: str, args: List[Expr] = None):
        self.name = name
        self.args = args or []


class BinOp(Expr):
    def __init__(self, left: Expr, op, right: Expr):
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(Expr):
    def __init__(self, op, expr: Expr):
        self.op = op
        self.expr = expr


class ListExpr(Expr):
    def __init__(self, elements: List[Expr]):
        self.elements = elements


class Name(Expr):
    def __init__(self, name: str):
        self.name = name


class Constant(Expr):
    def __init__(self, value: Any):
        self.value = value
