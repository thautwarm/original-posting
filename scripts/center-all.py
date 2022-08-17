from __future__ import annotations
from original_posting.types import CommandEntry, Context, OPDocument
from original_posting.parsing import process_nest
import bs4
import wisepy2

style_sheet = """
body {{
    word-wrap: break-word;
    max-width: {}px;
    margin: 10%;
}}
"""

def parse_args(*, width: int = 1200):
    return width

class AddStyleSheet:
    def __init__(self, width: int):
        self.width = width
    def __call__(self, op: OPDocument):
        html = bs4.BeautifulSoup(op.code, "html.parser")
        style = html.new_tag("style")
        style.contents.append(bs4.Stylesheet(style_sheet.format(self.width)))
        head = html.find("head")
        if isinstance(head, bs4.Tag):
            head.contents.append(style)
        else:
            html.contents.insert(0, style)
        op.code = str(html)
class ContainerHtml(CommandEntry):
    _inc = 0
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, argv: list[str], start: int, end: int):
        width = wisepy2.wise(parse_args)(argv)
        self.ctx.target_doc.callbacks.append(AddStyleSheet(width))
        return ''
