from __future__ import annotations
from original_posting.types import CommandEntry, Context, OPDocument
from original_posting.parsing import process_nest
from json import dumps
from xml.sax.saxutils import escape

class FootRefCmd(CommandEntry):
    _inc = 0
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, argv: list[str], start: int, end: int):
        title = process_nest(self.ctx, start, end).strip()
        tag = dumps("#" + title)
        return f"<sup href={tag}>{escape(title)}</sup>"
