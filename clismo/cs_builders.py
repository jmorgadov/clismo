import clismo.cs_ast as ast

builders = {
    # -------------------------------------------------------------------------
    "program -> obj_def program": lambda s, p: ast.Program([s] + p.stmts),
    "program -> NEWLINE program": lambda n, p: p,
    "program -> EPS": lambda: ast.Program([]),
    # -------------------------------------------------------------------------
    "obj_def -> client_def": lambda c: c,
    "obj_def -> server_def": lambda s: s,
    "obj_def -> step_def": lambda s: s,
    "obj_def -> sim_def": lambda s: s,
    # -------------------------------------------------------------------------
    "client_def -> client NAME : obj_def_body": lambda c, n, c2, b: ast.ClientDef(
        n.value, b
    ),
    "server_def -> server NAME : obj_def_body": lambda s, n, s2, b: ast.ServerDef(
        n.value, b
    ),
    "step_def -> step NAME : obj_def_body": lambda s, n, s2, b: ast.StepDef(n.value, b),
    "sim_def -> simulation NAME : obj_def_body": (
        lambda s, n, s2, b: ast.SimulationDef(n.value, b)
    ),
    # -------------------------------------------------------------------------
    "obj_def_body -> NEWLINE INDENT obj_stmt_list DEDENT": lambda n, i, l, d: l,
    # -------------------------------------------------------------------------
    "obj_stmt_list -> obj_stmt obj_stmt_list": lambda s, l: [s] + l,
    "obj_stmt_list -> NEWLINE obj_stmt_list": lambda s, l: l,
    "obj_stmt_list -> EPS": lambda: [],
    # -------------------------------------------------------------------------
    "obj_stmt -> NAME = test": lambda n, e, t: ast.Attr(n.value, t),
    "obj_stmt -> func_def": lambda f: f,
    # -------------------------------------------------------------------------
    "suite -> NEWLINE INDENT stmt_list DEDENT": lambda n, i, l, d: l,
    # -------------------------------------------------------------------------
    "func_def -> NAME ( name_list ) : suite": lambda n, p, a, p2, c, b: ast.Function(
        n.value, a, b
    ),
    # -------------------------------------------------------------------------
    "name_list -> NAME name_list": lambda n, l: [n.value] + l,
    "name_list -> EPS": lambda: [],
    # -------------------------------------------------------------------------
    "stmt_list -> stmt stmt_list": lambda s, l: [s] + l,
    "stmt_list -> NEWLINE stmt_list": lambda n, l: l,
    "stmt_list -> EPS": lambda: [],
    # -------------------------------------------------------------------------
    "stmt -> decl_stmt": lambda a: a,
    "stmt -> assign_stmt": lambda a: a,
    "stmt -> if_stmt": lambda i: i,
    "stmt -> loop_stmt": lambda l: l,
    "stmt -> return_stmt": lambda r: r,
    "stmt -> flow_stmt": lambda f: f,
    "stmt -> call": lambda c: c,
    # -------------------------------------------------------------------------
    "decl_stmt -> var NAME = test": lambda v, n, e, t: ast.Assign(n.value, t, True),
    # -------------------------------------------------------------------------
    "assign_stmt -> NAME = test": lambda n, e, t: ast.Assign(n.value, t),
    # -------------------------------------------------------------------------
    "if_stmt -> if test : suite": lambda i, t, b: ast.If(t, b),
    "if_stmt -> if test : suite else : suite": lambda i, t, b, e, b2: ast.If(t, b, b2),
    # -------------------------------------------------------------------------
    "loop_stmt -> loop : suite": lambda l, c, b: ast.Loop(None, b),
    "loop_stmt -> loop NAME : suite": lambda l, n, c, b: ast.Loop(n.value, b),
    "loop_stmt -> loop NAME from test : suite": (
        lambda l, n, f, t, c, b: ast.Loop(n.value, b, start=t)
    ),
    "loop_stmt -> loop NAME from test to test : suite": (
        lambda l, n, f, t1, t, t2, c, b: ast.Loop(n.value, b, start=t1, end=t2)
    ),
    "loop_stmt -> loop NAME from test to test by test : suite": (
        lambda l, n, f, t1, t, t2, by, t3, c, b: ast.Loop(
            n.value, b, start=t1, end=t2, step=t3
        )
    ),
    # -------------------------------------------------------------------------
    "flow_stmt -> endloop": lambda e: ast.EndLoop(),
    "flow_stmt -> nextloop": lambda n: ast.NextLoop(),
    # -------------------------------------------------------------------------
    "return_stmt -> return test": lambda r, t: ast.Return(t),
    # -------------------------------------------------------------------------
    "test -> or_test": lambda o: o,
    # -------------------------------------------------------------------------
    "or_test -> and_test": lambda a: a,
    "or_test -> and_test or or_test": (
        lambda a, o, o2: ast.BinOp(a, ast.Operator.OR, o2)
    ),
    # -------------------------------------------------------------------------
    "and_test -> not_test": lambda n: n,
    "and_test -> not_test and and_test": (
        lambda n, a, a2: ast.BinOp(n, ast.Operator.AND, a2)
    ),
    # -------------------------------------------------------------------------
    "not_test -> not not_test": lambda n, t: ast.UnaryOp(ast.Operator.NOT, t),
    "not_test -> comparison": lambda c: c,
    # -------------------------------------------------------------------------
    "comparison -> expr": lambda e: e,
    "comparison -> expr comp_op comparison": lambda l, o, r: ast.BinOp(l, o, r),
    # -------------------------------------------------------------------------
    "comp_op -> <": lambda c: ast.Operator.LT,
    "comp_op -> >": lambda c: ast.Operator.GT,
    "comp_op -> ==": lambda c: ast.Operator.EQ,
    "comp_op -> >=": lambda c: ast.Operator.GTE,
    "comp_op -> <=": lambda c: ast.Operator.LTE,
    "comp_op -> !=": lambda c: ast.Operator.NOT_EQ,
    # -------------------------------------------------------------------------
    "expr -> xor_expr": lambda x: x,
    "expr -> xor_expr | expr": (lambda l, o, r: ast.BinOp(l, ast.Operator.BIT_OR, r)),
    # -------------------------------------------------------------------------
    "xor_expr -> and_expr": lambda a: a,
    "xor_expr -> and_expr ^ xor_expr": (
        lambda l, o, r: ast.BinOp(l, ast.Operator.BIT_XOR, r)
    ),
    # -------------------------------------------------------------------------
    "and_expr -> shift_expr": lambda s: s,
    "and_expr -> shift_expr & and_expr": (
        lambda l, o, r: ast.BinOp(l, ast.Operator.BIT_AND, r)
    ),
    # -------------------------------------------------------------------------
    "shift_expr -> arith_expr": lambda a: a,
    "shift_expr -> arith_expr << shift_expr": (
        lambda l, o, r: ast.BinOp(l, ast.Operator.LSHIFT, r)
    ),
    "shift_expr -> arith_expr >> shift_expr": (
        lambda l, o, r: ast.BinOp(l, ast.Operator.RSHIFT, r)
    ),
    # -------------------------------------------------------------------------
    "arith_expr -> term": lambda t: t,
    "arith_expr -> term + arith_expr": (
        lambda l, o, r: ast.BinOp(l, ast.Operator.ADD, r)
    ),
    "arith_expr -> term - arith_expr": (
        lambda l, o, r: ast.BinOp(l, ast.Operator.SUB, r)
    ),
    # -------------------------------------------------------------------------
    "term -> factor": lambda f: f,
    "term -> factor * term": lambda l, o, r: ast.BinOp(l, ast.Operator.MUL, r),
    "term -> factor / term": lambda l, o, r: ast.BinOp(l, ast.Operator.DIV, r),
    "term -> factor % term": lambda l, o, r: ast.BinOp(l, ast.Operator.MOD, r),
    "term -> factor // term": (lambda l, o, r: ast.BinOp(l, ast.Operator.FLOORDIV, r)),
    # -------------------------------------------------------------------------
    "factor -> + factor": lambda o, f: ast.UnaryOp(ast.Operator.UADD, f),
    "factor -> - factor": lambda o, f: ast.UnaryOp(ast.Operator.USUB, f),
    "factor -> ~ factor": lambda o, f: ast.UnaryOp(ast.Operator.INVERT, f),
    "factor -> power": lambda p: p,
    # -------------------------------------------------------------------------
    "power -> atom": lambda a: a,
    "power -> atom ** factor": (lambda l, o, r: ast.BinOp(l, ast.Operator.POW, r)),
    # -------------------------------------------------------------------------
    "atom -> [ test_list ]": lambda c1, e, c2: ast.ListExpr(e),
    "atom -> [ ]": lambda p1, p2: ast.ListExpr([]),
    "atom -> NAME": lambda n: ast.Name(n.value),
    "atom -> NUMBER": lambda n: ast.Constant(
        int(n.value) if n.value.isnumeric() else float(n.value)
    ),
    "atom -> STRING": lambda s: ast.Constant(s.value),
    "atom -> None": lambda n: ast.Constant(None),
    "atom -> True": lambda t: ast.Constant(True),
    "atom -> False": lambda f: ast.Constant(False),
    "atom -> call": lambda c: c,
    # -------------------------------------------------------------------------
    "call -> NAME ( )": lambda n, p1, p2: ast.Call(n.value),
    "call -> NAME ( test_list )": lambda n, p1, a, p2: ast.Call(n.value, a),
    # -------------------------------------------------------------------------
    "test_list -> test": lambda t: [t],
    "test_list -> test , test_list": lambda t, o, tl: [t] + tl,
    # -------------------------------------------------------------------------
}
