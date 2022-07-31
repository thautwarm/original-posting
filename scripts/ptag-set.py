from __future__ import annotations
from original_posting import CommandEntry, Context, process_nest
from original_posting.ptag_dsl import string_to_expr_code, string_expr_builder
import original_posting.builtin_names as names


class PTagSetEntry(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, argv: list[str], start: int, end: int):
        ctx = self.ctx
        scope = ctx.storage.setdefault(names.NAME_PythonScope, {})
        rootdir = ctx.storage[names.NAME_Rootdir]
        cur_doc_tags = ctx.target_doc.tags
        source = process_nest(self.ctx, start, end)

        def __ptag_add(x):
            if x is not None:
                cur_doc_tags.append(x)

        scope["__ptag_add"] = __ptag_add

        exec(string_expr_builder(source), scope)
        return ""

    def inline_proc(self, _start: int, _stop: int) -> str:
        ctx = self.ctx
        scope = ctx.storage.setdefault(names.NAME_PythonScope, {})
        cur_doc_tags = ctx.target_doc.tags
        source = process_nest(self.ctx, _start, _stop)

        v = eval(string_to_expr_code(source), scope)
        if v is not None:
            cur_doc_tags.append(v)
        return ""
