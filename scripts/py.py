from contextlib import redirect_stdout
from original_posting import CommandEntry, Context, process_nest
import original_posting.builtin_names as names
import io


class PyIO(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, args: list[str], _start: int, _stop: int) -> str:
        use_expr = "expr" in args
        code = process_nest(self.ctx, _start, _stop)
        scope = self.ctx.storage.setdefault(names.NAME_PythonScope, {})
        if use_expr:
            code = code.strip()
            bc = compile(code, self.ctx.file, mode="eval")
            try:
                return str(eval(bc, scope))
            except:
                raise ValueError(code)
        if code.startswith(" "):
            code = "if True:\n%s" % code
        out = io.StringIO()
        with redirect_stdout(out):
            bc = compile(code, self.ctx.file, mode="exec")
            exec(bc, scope)
        return out.getvalue()

    def inline_proc(self, start: int, end: int):
        return self.proc(["expr"], start, end)
