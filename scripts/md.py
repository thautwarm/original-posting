from original_posting.types import CommandEntry, Context
from original_posting.parsing import process_nest
import markdown2


class Md2Html(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, args: list[str], _start: int, _stop: int) -> str:
        return markdown2.markdown(process_nest(self.ctx, _start, _stop))
