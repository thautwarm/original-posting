from __future__ import annotations
from original_posting.types import Runtime, CommandEntry, Context, OPDocument
from original_posting.parsing import process_nest
from json import dumps
from xml.sax.saxutils import escape
import bs4



FootNoteId = str
FootNoteContent = str

_html_factory = bs4.BeautifulSoup("", "html.parser")

class FootNoteCmd(CommandEntry):
    _inc = 0
    def __init__(self, ctx: Context):
        self.ctx = ctx

    @staticmethod
    def callback(op_doc: OPDocument):
        inserted_footnodes: list[tuple[FootNoteId, FootNoteContent]]
        inserted_footnodes =  op_doc.data.setdefault(FootNoteCmd, [])
        # TODO: html ast
        hr = _html_factory.new_tag("hr")
        h2 = _html_factory.new_tag("h2")
        h2.append("脚注")
        ol = _html_factory.new_tag("ol")
        for (title, content) in inserted_footnodes:
            li = _html_factory.new_tag("li")
            li.append(escape(title))
            li.append(":")
            li.attrs["id"] = title
            p = _html_factory.new_tag("p")
            li.contents.append(p)
            p = _html_factory.new_tag("p")
            p.contents.extend(bs4.BeautifulSoup("<div>"+content+"</div>", "html.parser").contents[0].contents) # type: ignore
            li.contents.append(p)
            ol.contents.append(li)
        op_doc.code += '\n' + str(hr) + "\n" + str(h2) + "\n" + str(ol)


    def proc(self, argv: list[str], start: int, end: int):
        title_end = self.ctx.source.find(':', start, end)
        if title_end != -1:
            title = self.ctx.source[start:title_end].strip()
        else:
            self._inc += 1
            title = f'footnote{self._inc}'
        content = process_nest(self.ctx, title_end+1, end).strip()
        inserted_footnodes: list[tuple[FootNoteId, FootNoteContent]]
        inserted_footnodes= self.ctx.target_doc.data.setdefault(FootNoteCmd, [])
        inserted_footnodes.append((title, content))
        if self.callback not in self.ctx.target_doc.callbacks:
            self.ctx.target_doc.callbacks.append(self.callback)
        a = _html_factory.new_tag("a", href="#" + title)
        sup = _html_factory.new_tag("sup")
        small2 = _html_factory.new_tag("small")
        small = _html_factory.new_tag("small")
        small2.contents.append(small)
        small.append(escape(title))
        sup.contents.append(small2)
        a.append(sup)
        return str(a)
