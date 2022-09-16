from __future__ import annotations
from xml.sax.saxutils import escape
from original_posting.types import CommandEntry, Context, OPDocument
from original_posting.parsing import process_nest
import wisepy2
import bs4

_html_factory = bs4.BeautifulSoup("", "html.parser")

class RawLink(CommandEntry):
    _inc = 0
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, argv: list[str], start: int, end: int):
        raise NotImplementedError

    def inline_proc(self, start: int, end: int):
        link = process_nest(self.ctx, start, end)
        a = _html_factory.new_tag("a", attrs={'href': link})
        a.append(escape(link))
        return str(a)
