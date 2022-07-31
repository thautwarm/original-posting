from __future__ import annotations
import pathlib
from original_posting.parsing import process_nest
from original_posting.ptag_dsl import P, string_pattern_builder, cps_and, match_any_tag, string_to_pattern
from original_posting.types import OPDocument, CommandEntry, Context
from original_posting.utils import get_project_based_path, global_gensym
import original_posting.builtin_names as names
import functools
import bs4


class FilterIndex:
    def __init__(self, pattern: P, html_id: str):
        self.P = pattern
        self.html_id = html_id

    def __call__(self, doc: OPDocument):
        html = bs4.BeautifulSoup(doc.code, "html.parser")
        ul = html.find("ul", attrs={"id": self.html_id})
        if not ul:
            return

        for each in doc.project_docs.values():
            each.working_dir_absolute

            if match_any_tag(self.P, each.tags):
                path = str(pathlib.Path(each.project_based_path).with_suffix(".html"))
                title = each.title or each.output_path_absolute.name
                li = html.new_tag("li")
                a = html.new_tag("a", href=path)
                a.append(title)
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
        source = process_nest(self.ctx, start, end)
        patterns = string_pattern_builder(source)
        if not patterns:
            raise ValueError("At least one pattern is required.")
        matcher = functools.reduce(cps_and, patterns)
        html_id = global_gensym("filtered-index")
        ctx.target_doc.callbacks.append(FilterIndex(matcher, html_id))
        return f'<ul id="{html_id}"></ul>'

    def inline_proc(self, _start: int, _stop: int) -> str:
        ctx = self.ctx
        source = process_nest(self.ctx, _start, _stop)
        pattern = string_to_pattern(source)
        html_id = global_gensym("filtered-index")
        ctx.target_doc.callbacks.append(FilterIndex(pattern, html_id))
        return f'<ul id="{html_id}"></ul>'
