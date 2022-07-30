from __future__ import annotations
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from original_posting import CommandEntry, Context, load_from_source, process_nest
from wisepy2 import wise
import pathlib
import typing

if typing.TYPE_CHECKING:
    from .pygments_styles import quiet_light as mod
else:
    mod = load_from_source(
        str(pathlib.Path(__file__).parent / "pygments_styles" / "quiet_light.py")
    )


def parse_args(*, lang: str = "", mkstyle: bool = False):
    return dict(lang=lang, mkstyle=mkstyle)


class CodeHighlightEntry(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, args: list[str], _start: int, _stop: int) -> str:
        opts: dict = wise(parse_args)(args)  # type: ignore
        formatter = HtmlFormatter(style=mod.quiet_light)
        if opts["mkstyle"]:
            if opts["lang"]:
                raise ValueError("--lang and --mkstyle are exclusive.")
            return "<style>\n" + formatter.get_style_defs() + "\n</style>"
        lang = opts["lang"]
        store = self.ctx.storage.setdefault(CodeHighlightEntry, {})
        if not lang:
            if not store.get("lang"):
                raise ValueError("--lang is required.")
            else:
                lang = store["lang"]
        else:
            lang = store["lang"] = str(lang)

        code = process_nest(self.ctx, _start, _stop)
        lexer = get_lexer_by_name(lang)
        return highlight(code, lexer, formatter)

    def inline_proc(self, _start: int, _end: int):
        store = self.ctx.storage.get(CodeHighlightEntry)
        if not store or not store.get("lang"):
            raise ValueError(
                "--lang is not set. You might need to call '@begin code --lang xxx' firstly."
            )

        lang = store["lang"]
        formatter = HtmlFormatter(style=mod.quiet_light)
        code = process_nest(self.ctx, _start, _end)
        lexer = get_lexer_by_name(lang)
        return highlight(code, lexer, formatter)
