from original_posting import CommandEntry, Context


class PlainCommand(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, args: list[str], _start: int, _stop: int) -> str:
        return self.ctx.source[_start:_stop]
