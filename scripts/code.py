from __future__ import annotations
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from original_posting.utils import load_from_source
from original_posting.types import CommandEntry, Context, OPDocument
from original_posting.parsing import process_nest
from wisepy2 import wise
import pathlib
import typing
import bs4

if typing.TYPE_CHECKING:
    from .pygments_styles import quiet_light as mod
else:
    mod = load_from_source(
        str(pathlib.Path(__file__).parent / "pygments_styles" / "quiet_light.py")
    )


def parse_args(lang: str = ""):
    return lang


class InsertStyle:
    def __init__(self, lazy_style_sheet: typing.Callable[[], str]):
        self.lazy_style_sheet = lazy_style_sheet

    def __call__(self, doc: OPDocument):
        style_inserted = doc.data.setdefault(InsertStyle, False)
        if not style_inserted:
            html = bs4.BeautifulSoup(doc.code, "html.parser")
            style_node = html.find("style")
            if not style_node:
                style_node = html.new_tag("style")
                html.insert(0, style_node)
            style_node.append(self.lazy_style_sheet())
            doc.data[InsertStyle] = True
            doc.code = str(html)


class CachedLanguageKey:
    pass


class CodeHighlightEntry(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, args: list[str], _start: int, _end: int) -> str:
        lang = wise(parse_args)(args)
        local_data = self.ctx.target_doc.data
        if not lang:
            lang = local_data.get(CachedLanguageKey)
            if not lang:
                raise ValueError(
                    "--lang is not set. You might need to call '@begin code language' firstly."
                )
        else:
            local_data[CachedLanguageKey] = lang

        return self._impl(_start, _end, False)

    def inline_proc(self, _start: int, _end: int):
        return self._impl(_start, _end, True)

    def _impl(self, start: int, end: int, inline: bool) -> str:
        local_data = self.ctx.target_doc.data
        lang = local_data.get(CachedLanguageKey)
        if not lang:
            raise ValueError(
                "--lang is not set. You might need to call '@begin code language' firstly."
            )

        formatter = HtmlFormatter(style=mod.quiet_light)
        self.ctx.target_doc.callbacks.append(InsertStyle(formatter.get_style_defs))

        code = process_nest(self.ctx, start, end)
        lexer = get_lexer_by_name(lang)
        hightlighted_code = highlight(code, lexer, formatter)
        if inline:
            html = bs4.BeautifulSoup(hightlighted_code)
            pre = html.find("pre")
            assert isinstance(pre, bs4.Tag)
            code_tag = html.new_tag("code")
            code_tag.extend(pre.contents)
            return str(code_tag)
        return hightlighted_code
