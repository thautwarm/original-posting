from contextlib import redirect_stdout
from original_posting import CommandEntry, Context, process_nest
import original_posting.builtin_names as names
import io


class TestCmd(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, args: list[str], _start: int, _stop: int) -> str:
        print(_start, _stop)
        _stop = self.ctx.source.rindex('\n', _start + 1, _stop)
        return repr(self.ctx.source[_start:_stop])
