from __future__ import annotations
import textwrap
from typing import Sequence
from collections import ChainMap
import builtins
import ast
import functools
import typing


P = typing.Callable[[object, dict], bool]


def cps_capture(id: str) -> P:
    def apply(o, scope):
        scope[id] = o
        return True

    return apply


def cps_seq(p_elts: Sequence[P]) -> P:
    def apply(o, scope):
        if not isinstance(o, Sequence):
            return False
        if len(o) != len(p_elts):
            return False
        for (each, p) in zip(o, p_elts):
            if not p(each, scope):
                return False
        return True

    return apply


def cps_seq3(p_init: Sequence[P], p_pack: P, p_tail) -> P:
    def apply(o, scope):
        if not isinstance(o, Sequence):
            return False
        if len(o) < len(p_init) + len(p_tail):
            return False
        for i in range(0, len(p_init)):
            p = p_init[i]
            if not p(o[i], scope):
                return False
        for i in range(0, len(p_tail)):
            p = p_tail[i]
            if not p(o[i + len(o) - len(p_tail)], scope):
                return False
        return p_pack(o[len(p_init) : len(o) - len(p_tail)], scope)

    return apply


def cps_literal(v) -> P:
    def apply(o, scope):
        return o == v

    return apply

def cps_not(p: P) -> P:
    def apply(o, scope):
        return not p(o, {**scope})
    return apply

_undef = object()


def cps_deconstruct(p_name: P, p_args: list[P]) -> P:
    def apply(o, scope):
        if not isinstance(o, dict):
            return False
        v = o.get("__func__", _undef)
        if v is _undef:
            return False
        args = o.get("__args__", _undef)
        if args is _undef or not isinstance(args, list):
            return False
        if len(args) != len(p_args):
            return False
        if not p_name(v, scope):
            return False
        for (each, p) in zip(args, p_args):
            if not p(each, scope):
                return False
        return True

    return apply


def cps_dict(kv: list[tuple[object, P]]) -> P:
    def apply(o, scope):
        if not isinstance(o, dict):
            return False
        for (k, p) in kv:
            if not p(o[k], scope):
                return False
        return True

    return apply


def cps_typecheck(t: type):
    def apply(o, scope):
        return isinstance(o, t)

    return apply


def cps_or(p1: P, p2: P):
    def apply(o, scope):
        return p1(o, scope) or p2(o, scope)

    return apply


def cps_and(p1: P, p2: P):
    def apply(o, scope):
        return p1(o, scope) and p2(o, scope)

    return apply


def cps_and_seq(p1: P, p2: P):
    def apply(o, scope):
        if not isinstance(o, list):
            return False
        l = False
        r = False
        for each in o:
            if l and r:
                return True
            if not l and p1(each, scope):
                l = True
            if not r and p2(each, scope):
                r = True
        return l and r

    return apply


def cps_predicate(f):
    def apply(o, scope):
        return f(o, scope)

    return apply


def cps_wildcard(o, scope):
    return True


class PTagPredicationBuilder(ast.NodeTransformer):
    def visit_slice(self, node: ast.slice):
        """Python 3.7 compat"""
        if isinstance(node, ast.Index):
            return node.value  # type: ignore
        if isinstance(node, ast.ExtSlice):
            return ast.Tuple(
                list(map(self.visit_slice, node.dims)),  # type: ignore
                ast.Load(),
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        raise TypeError(f"slice: {node} is not supported")


class PTagPatternBuilder(ast.NodeTransformer):
    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, None)
        if not visitor:
            raise TypeError(f"{node.__class__.__name__} is not supported")
        return visitor(node)

    def visit_Subscript(self, node: ast.Subscript):
        assert (
            isinstance(node.value, ast.Name) and node.value.id == "P"
        ), "only predicate in form of 'P[expr]' is supported"

        n: ast.expr = PTagPredicationBuilder().visit(node.slice)

        if isinstance(n, ast.Tuple):
            condition: ast.expr = ast.BoolOp(
                op=ast.And(),
                values=list(n.elts),
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        else:
            condition = n

        expr_node = ast.Expression(condition)
        ast.fix_missing_locations(expr_node)
        c = compile(expr_node, "<string>", "eval")

        def predicate(o, scope):
            local_dict = {"_": o}
            return eval(c, builtins.__dict__, ChainMap(local_dict, scope))

        return cps_predicate(predicate)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        if isinstance(node.op, ast.Invert):
            v = node.operand
            if isinstance(v, ast.Name):
                return cps_capture(v.id)
            raise ValueError(f"~x: x needs to be a name but got {v}")
        if isinstance(node.op, ast.Not):
            v = node.operand
            return cps_not(self.visit(v))
        raise ValueError(f"UnaryOp: {node.op} is not supported")

    def visit_Name(self, node: ast.Name):
        if node.id == "_":
            return cps_wildcard
        return cps_literal(node.id)

    def visit_BoolOp(self, node: ast.BoolOp):
        if isinstance(node.op, ast.Or):
            return functools.reduce(cps_or, map(self.visit, node.values))
        if isinstance(node.op, ast.And):
            return functools.reduce(cps_and, map(self.visit, node.values))
        raise ValueError(f"BoolOp: {node.op} is not supported")

    def visit_Constant(self, node: ast.Constant):
        return cps_literal(node.value)

    visit_Str = visit_Bytes = visit_Num = visit_NamedConstant = visit_Constant

    def visit_List(self, node: ast.List):
        idx_pack = -1
        star: ast.Starred | None = None
        for i, e in enumerate(node.elts):
            if isinstance(e, ast.Starred):
                idx_pack = i
                star = e
        if idx_pack == -1:
            return cps_seq(list(map(self.visit, node.elts)))
        assert star
        return cps_seq3(
            list(map(self.visit, node.elts[:idx_pack])),
            self.visit(star.value),
            list(map(self.visit, node.elts[idx_pack + 1 :])),
        )

    def visit_Dict(self, node: ast.Dict):
        keys: list[object] = []
        for k in node.keys:
            if k is None:
                raise SyntaxError("Dict packing is not supported yet")
            if isinstance(k, ast.Name):
                k_value = k.id
            elif not isinstance(k, ast.Constant):
                raise SyntaxError("Dict keys must be constant")
            else:
                k_value = k.value
            keys.append(k_value)
        return cps_dict([(k, self.visit(v)) for (k, v) in zip(keys, node.values)])

    def visit_Call(self, node: ast.Call):
        if node.keywords:
            raise SyntaxError("Keyword arguments are not supported")
        func = self.visit(node.func)
        args = list(map(self.visit, node.args))
        return cps_deconstruct(func, args)


class PTagPatternConjunction(ast.NodeVisitor):
    def __init__(self):
        self.result = []

    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, None)
        if not visitor:
            raise TypeError(f"{node.__class__.__name__} is not supported")
        return visitor(node)

    def visit_Expr(self, node: ast.Expr):
        value = PTagPatternBuilder().visit(node.value)
        self.result.append(value)
        return node

    def visit_Module(self, node: ast.Module):
        for each in node.body:
            self.visit(each)


def parse_expr(code: str):
    body = ast.parse(code).body
    if len(body) != 1:
        raise SyntaxError("Expected a single expression")
    stmt = body[0]
    if not isinstance(stmt, ast.Expr):
        raise SyntaxError("Expected an expression")
    return stmt.value


class PTagExprBuilder(ast.NodeTransformer):
    def visit_Name(self, node: ast.Name):
        return ast.Constant(node.id, lineno=node.lineno, col_offset=node.col_offset)

    def visit_Call(self, node: ast.Call):
        if node.keywords:
            raise SyntaxError("Keyword arguments are not supported")
        func = self.visit(node.func)
        args = list(map(self.visit, node.args))
        return ast.Dict(
            [ast.Constant("__func__"), ast.Constant("__args__")],
            [
                func,
                ast.List(
                    args, ast.Load(), line=node.lineno, col_offset=node.col_offset
                ),
            ],
        )


class PTagExprDisjunctionBuilder(ast.NodeTransformer):
    def visit_Expr(self, node: ast.Expr):
        append_func = ast.Name(
            "__ptag_add", ast.Load(), lineno=node.lineno, col_offset=node.col_offset
        )
        value = PTagExprBuilder().visit(node.value)
        node.value = ast.Call(append_func, [value], [])
        return node


def string_to_expr_code(code: str):
    x = PTagExprBuilder().visit(parse_expr(code.strip()))
    x = ast.Expression(x)
    ast.fix_missing_locations(x)
    bc = compile(x, "<string>", "eval")
    return bc


def string_expr_builder(code: str):
    if code.startswith(" "):
        code = "if True:\n" + code
    x = PTagExprDisjunctionBuilder().visit(ast.parse(code))
    ast.fix_missing_locations(x)
    bc = compile(x, "<string>", "exec")
    return bc


def string_to_pattern(code: str) -> P:
    return PTagPatternBuilder().visit(parse_expr(code.strip()))


def string_pattern_builder(code: str) -> list[P]:
    if code.startswith(" "):
        code = textwrap.dedent(code)
    builder = PTagPatternConjunction()
    builder.visit(ast.parse(code))
    return builder.result


def match_tag(p: P, o: object, group: dict | None = None) -> bool:
    if group is None:
        group = {}
    return p(o, group)


def match_any_tag(p: P, obs: list[object], group: dict | None = None) -> bool:
    if group is None:
        group = {}
    for o in obs:
        if p(o, group):
            return True
    return False


if __name__ == "__main__":
    x = parse_expr("[1, 2, a(c, 2)]")
    x = PTagExprBuilder().visit(x)
    ast.fix_missing_locations(x)

    z = eval(compile(ast.Expression(x), "<string>", "eval"), globals())
    if False:

        print(z)

        x = parse_expr("[1, 2,  (~a)(~c, 2) or ~a]")

        f = PTagPatternBuilder().visit(x)

        # data = [1, 2, {'__func__': 'a', '__args__': [1, 2]}]
        scope = {}
        print(f(z, scope))
        print(scope)

        __ptag_add = lambda x: print(x)
        mod = PTagExprDisjunctionBuilder().visit(ast.parse("k(1)"))
        ast.fix_missing_locations(mod)
        exec(compile(mod, "<string>", "exec"), globals())

    z = eval(string_to_expr_code("[1, 2, a(c, 2)]"))
    p = string_to_pattern("[1, *~args, a(~c, 2)] and P[c == 'c']")
    scope = {}
    print("predicate match:", match_tag(p, z, scope), scope)
