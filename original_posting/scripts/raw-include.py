from __future__ import annotations
from xml.sax.saxutils import escape
from original_posting.types import CommandEntry, Context, OPDocument, Scope
from original_posting.parsing import process_nest, new_context
from original_posting.utils import get_relative_path
import bs4


class RawInclude(CommandEntry):
    _inc = 0
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, argv: list[str], start: int, end: int):
        raise NotImplementedError

    def inline_proc(self, start: int, end: int):
        cur_doc = self.ctx.target_doc
        file = process_nest(self.ctx, start, end)
        file = self.ctx.target_doc.working_dir_absolute.joinpath(file).absolute()
        proj_based_path = get_relative_path(file, cur_doc.project_path_absolute)
        old_project_based_path = cur_doc.project_based_path
        old_project_path_absolute = cur_doc.project_path_absolute
        old_working_dir_absolute = cur_doc.working_dir_absolute
        old_ctx = self.ctx
        try:
            cur_doc.project_based_path = proj_based_path
            cur_doc.project_path_absolute = file
            cur_doc.working_dir_absolute = file.parent
            new_ctx = new_context(
                file.as_posix(),
                file.read_text(encoding='utf-8'),
                self.ctx.storage,
                cur_doc
            )
            self.ctx = new_ctx
            new_ctx.cur_scope = Scope(
                "raw-include",
                self,
                0,
                [],
                0,
                0
            )
            s =  process_nest(new_ctx, 0, len(new_ctx.source))
            return s
        finally:
            cur_doc.project_based_path = old_project_based_path
            cur_doc.project_path_absolute = old_project_path_absolute
            cur_doc.working_dir_absolute = old_working_dir_absolute
            self.ctx = old_ctx
