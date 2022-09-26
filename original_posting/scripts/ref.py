from __future__ import annotations
from sqlite3 import connect
from original_posting.types import Runtime, CommandEntry, Context, OPDocument
from original_posting.parsing import process_nest, get_command_entry
from json import dumps
from xml.sax.saxutils import escape
from wisepy2 import wise
import shlex
import typing
import bs4

class ParseArgs(typing.TypedDict):
    mode: typing.Literal['mk', 'use']
    title: str

class ArgParser:
    @staticmethod
    def mk():
        return ParseArgs(mode='mk', title='')
    @staticmethod
    def use(title: str):
        return ParseArgs(mode='use', title=title.strip())

FootNoteId = str
FootNoteContent = str

_html_factory = bs4.BeautifulSoup("", "html.parser")

class RFootNoteCmd(CommandEntry):
    _inc = 0
    def __init__(self, ctx: Context):
        self.ctx = ctx

    @staticmethod
    def callback(op_doc: OPDocument):
        inserted_footnodes: dict[FootNoteId, FootNoteContent]
        inserted_footnodes = op_doc.data.setdefault(RFootNoteCmd, {})
        html = bs4.BeautifulSoup(op_doc.code, "html.parser")
        # TODO: html ast
        ol = _html_factory.new_tag("ol")
        order: dict[FootNoteId, int] = {}
        for i, (title, content) in enumerate(inserted_footnodes.items()):
            order[title] = i + 1
            li = _html_factory.new_tag("li")
            li.attrs["id"] = title
            p = _html_factory.new_tag("p")
            p.contents.extend(bs4.BeautifulSoup("<div>" + content + "<div>", "html.parser").contents[0].contents) # type: ignore
            li.contents.append(p)
            ol.contents.append(li)

        ol = bs4.BeautifulSoup(str(ol), "html.parser")
        for tag in ol, html:
            for each in tag.find_all("a", attrs={"unsolved-kind": "rfootnote-ref"}):
                if not isinstance(each, bs4.element.Tag):
                    continue
                del each.attrs['unsolved-kind']
                i = order.get(each.attrs['href'][1:])
                if i:
                    each.append(f"[{i}]")

        for each in html.find_all("div", attrs={"unsolved-kind": "rfootnote-mk"}):
            if not isinstance(each, bs4.element.Tag):
                continue
            del each.attrs['unsolved-kind']
            each.contents.append(ol)

        op_doc.code = str(html)

    def proc(self, argv: list[str], start: int, end: int):
        title = argv[0].strip()
        content = process_nest(self.ctx, start, end).strip()
        inserted_footnodes: dict[FootNoteId, FootNoteContent]
        inserted_footnodes= self.ctx.target_doc.data.setdefault(RFootNoteCmd, {})
        inserted_footnodes[title] = content
        if self.callback not in self.ctx.target_doc.callbacks:
            self.ctx.target_doc.callbacks.append(self.callback)
        return ''

    def inline_proc(self, start: int, end: int):
        args = shlex.split(process_nest(self.ctx, start, end))
        args = typing.cast(ParseArgs, wise(ArgParser)(args))

        mode = args['mode']
        if mode == 'mk':
            div = _html_factory.new_tag("div", attrs={"unsolved-kind": "rfootnote-mk"})
            return str(div)
        elif mode == 'use':
            title = args['title']
            a = _html_factory.new_tag("a", href="#" + title, attrs={"unsolved-kind": "rfootnote-ref"})
        else:
            raise ValueError("Unknown mode: " + mode)
        return str(a)