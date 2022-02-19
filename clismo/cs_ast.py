from __future__ import annotations

import enum
from typing import Any, List

from clismo.compiler.generic_ast import AST


class Operator(enum.Enum):
    ADD = enum.auto()
    SUB = enum.auto()
    MUL = enum.auto()
    DIV = enum.auto()
    MOD = enum.auto()
    POW = enum.auto()
    AND = enum.auto()
    OR = enum.auto()
    LSHIFT = enum.auto()
    RSHIFT = enum.auto()
    BIT_AND = enum.auto()
    BIT_XOR = enum.auto()
    BIT_OR = enum.auto()
    FLOORDIV = enum.auto()
    EQ = enum.auto()
    NOT_EQ = enum.auto()
    LT = enum.auto()
    LTE = enum.auto()
    GT = enum.auto()
    GTE = enum.auto()
    NOT = enum.auto()
    UADD = enum.auto()
    USUB = enum.auto()
    INVERT = enum.auto()


class Program(AST):
    __slots__ = ("stmts",)

    def __init__(self, stmts: List[ObjDef]):
        self.stmts = stmts


class ObjDef(AST):
    def __init__(
        self,
        obj_type: str,
        name: str,
        body: List[AST],
    ):
        self.obj_type = obj_type
        self.name = name
        self.body = body


class ClientDef(ObjDef):
    __slots__ = ("name", "body")

    def __init__(self, name, body):
        super().__init__("client", name, body)


class ServerDef(ObjDef):
    __slots__ = ("name", "body")

    def __init__(self, name, body):
        super().__init__("server", name, body)


class StepDef(ObjDef):
    __slots__ = ("name", "body")

    def __init__(self, name, body):
        super().__init__("step", name, body)


class SimulationDef(ObjDef):
    __slots__ = ("name", "body")

    def __init__(self, name, body):
        super().__init__("simulation", name, body)


class Attr(AST):
    __slots__ = ("name", "value")

    def __init__(self, name: str, value: Expr):
        self.name = name
        self.value = value


class Function(AST):
    __slots__ = ("name", "info", "body")

    def __init__(self, name: str, info: List[Name], body: List[Stmt]):
        self.name = name
        self.info = info
        self.body = body


class Stmt(AST):
    pass


class Assign(Stmt):
    __slots__ = ("name", "value", "decl")

    def __init__(self, name: str, value: Expr, decl: bool = False):
        self.name = name
        self.value = value
        self.decl = decl


class If(Stmt):
    __slots__ = ("cond", "then", "els")

    def __init__(self, cond: Expr, then: List[Stmt], els: List[Stmt] = None):
        self.cond = cond
        self.then = then
        self.els = els or []


class Return(Stmt):
    __slots__ = ("value",)

    def __init__(self, value: Expr):
        self.value = value


class Loop(Stmt):
    __slots__ = ("target", "start", "end", "step", "body")

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


class EndLoop(Stmt):
    pass


class NextLoop(Stmt):
    pass


class Expr(AST):
    pass


class Call(Expr):
    __slots__ = ("name", "args")

    def __init__(self, name: str, args: List[Expr] = None):
        self.name = name
        self.args = args or []


class BinOp(Expr):
    __slots__ = ("left", "op", "right")

    def __init__(self, left: Expr, op, right: Expr):
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(Expr):
    __slots__ = ("op", "expr")

    def __init__(self, op, expr: Expr):
        self.op = op
        self.expr = expr


class ListExpr(Expr):
    __slots__ = ("elements",)

    def __init__(self, elements: List[Expr]):
        self.elements = elements


class Name(Expr):
    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name

    def show(self):
        return f"Name: {self.name}"


class Constant(Expr):
    __slots__ = ("value",)

    def __init__(self, value: Any):
        self.value = value

    def show(self):
        return f"Constant: {self.value}"
