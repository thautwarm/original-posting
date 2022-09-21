from __future__ import annotations
import os
import pathlib
from typing import ChainMap
from original_posting.parsing import process_nest
from original_posting.ptag_dsl import (
    P,
    string_pattern_builder,
    cps_and,
    match_any_tag,
    string_to_pattern,
)
from original_posting.types import OPDocument, CommandEntry, Context
from original_posting.utils import get_relative_path, global_gensym
import original_posting.builtin_names as names
import functools
import bs4


def default_format(doc: OPDocument):
    return doc.title or doc.output_path_absolute.name


class FilterIndex:
    def __init__(self, ctx: Context, scope: dict, pattern: P, html_id: str):
        self.P = pattern
        self.html_id = html_id
        self.scope = scope
        self.ctx = ctx

    def __call__(self, doc: OPDocument):
        html = bs4.BeautifulSoup(doc.code, "html.parser")
        ul = html.find("ul", attrs={"id": self.html_id})
        if not ul:
            return
        format_func = self.ctx.storage.get(names.NAME_IndexFormatter, default_format)
        scope = ChainMap({}, self.scope)

        # TODO: use root directory of output path instead of project path
        parts1 = ('..', ) * (len(doc.output_path_absolute.relative_to(doc.project_path_absolute).parts) - 1)
        for each in doc.project_docs.values():

            if match_any_tag(self.P, each.tags, scope):  # type: ignore
                part2 = each.output_path_absolute.relative_to(doc.project_path_absolute).parts
                path = os.path.join(*parts1, *part2)
                # path = str(pathlib.Path(each.project_based_path).with_suffix(".html"))
                display_text = format_func(each) or default_format(each)
                li = html.new_tag("li")
                a = html.new_tag("a", href=path)
                a.append(display_text)
                li.append(a)
                ul.append(li)

        doc.code = str(html)


class PTagQueryDocsEntry(CommandEntry):
    """
    @begin ptag-filter
    @end ptag-filter
    """

    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, argv: list[str], start: int, end: int):
        ctx = self.ctx
        scope = self.ctx.storage.setdefault(names.NAME_PythonScope, {})
        source = process_nest(self.ctx, start, end)
        patterns = string_pattern_builder(source)
        if not patterns:
            raise ValueError("At least one pattern is required.")
        matcher = functools.reduce(cps_and, patterns)
        html_id = global_gensym("filtered-index")
        ctx.target_doc.callbacks.append(FilterIndex(self.ctx, scope, matcher, html_id))
        return f'<ul id="{html_id}"></ul>'

    def inline_proc(self, _start: int, _stop: int) -> str:
        ctx = self.ctx
        scope = self.ctx.storage.setdefault(names.NAME_PythonScope, {})
        source = process_nest(self.ctx, _start, _stop)
        pattern = string_to_pattern(source)
        html_id = global_gensym("filtered-index")
        ctx.target_doc.callbacks.append(FilterIndex(self.ctx, scope, pattern, html_id))
        return f'<ul id="{html_id}"></ul>'
