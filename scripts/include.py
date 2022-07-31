from original_posting.types import CommandEntry, Context
from original_posting.parsing import process_nest
import original_posting.builtin_names as names


class IncludeEntry(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def inline_proc(self, _start: int, _stop: int) -> str:
        source = process_nest(self.ctx, _start, _stop)
        include = self.ctx.storage[names.NAME_IncludeImpl]
        include(source.strip())
        return ""

    def proc(self, argv: list[str], start: int, end: int):
        raise SyntaxError("Use inline form: @include| dir/xxx.op |")

