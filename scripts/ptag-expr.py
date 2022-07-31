from __future__ import annotations
from original_posting.types import CommandEntry, Context
from original_posting.parsing import process_nest
from original_posting.ptag_dsl import string_to_expr_code
import original_posting.builtin_names as names


class PTagExprEntry(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, args: list[str], _start: int, _stop: int) -> str:
        source = process_nest(self.ctx, _start, _stop)
        scope: dict = self.ctx.storage.setdefault(names.NAME_PythonScope, {})
        PTAG_EXPRS = scope.setdefault(names.VARNAME_ptag_exprs, {})
        ptag_expr = eval(string_to_expr_code(source), scope)
        key = len(PTAG_EXPRS)
        PTAG_EXPRS[key] = ptag_expr
        return f"globals()['{names.VARNAME_ptag_exprs}'][{key}]"
