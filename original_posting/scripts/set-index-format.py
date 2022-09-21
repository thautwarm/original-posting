from original_posting.types import CommandEntry, Context
from original_posting.parsing import process_nest
import original_posting.builtin_names as names

class SetIndexFormat(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, args: list[str], _start: int, _stop: int) -> str:
        code = process_nest(self.ctx, _start, _stop)
        scope = self.ctx.storage.setdefault(names.NAME_PythonScope, {})
        code = code.strip()
        bc = compile(code, self.ctx.file, mode="eval")
        try:
            f = eval(bc, scope)
        except:
            raise ValueError(code)

        if not callable(f):
            raise ValueError('does not produce a function:' + code)
        self.ctx.storage[names.NAME_IndexFormatter] = f
        return ''
