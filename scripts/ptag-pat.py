from __future__ import annotations
from original_posting import CommandEntry, Context, process_nest
from original_posting.ptag_dsl import string_to_pattern
import original_posting.builtin_names as names


class PTagExprEntry(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, args: list[str], _start: int, _stop: int) -> str:
        source = process_nest(self.ctx, _start, _stop)
        scope: dict = self.ctx.storage.setdefault(names.NAME_PythonScope, {})
        PTAG_PATS = scope.setdefault(names.VARNAME_ptag_pats, {})
        ptag_pattern = string_to_pattern(source)
        key = len(PTAG_PATS)
        PTAG_PATS[key] = ptag_pattern
        return f"globals()['{names.VARNAME_ptag_pats}'][{key}]"
