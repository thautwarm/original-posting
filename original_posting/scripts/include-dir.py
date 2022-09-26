from original_posting.types import CommandEntry, Context
from original_posting.parsing import process_nest
import original_posting.builtin_names as names
from pathlib import Path


class IncludeDirEntry(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def inline_proc(self, _start: int, _stop: int) -> str:
        directory = Path(process_nest(self.ctx, _start, _stop).strip())
        for each in directory.iterdir():
            if each.is_file() and each.suffix == '.op':
                include = self.ctx.storage[names.NAME_IncludeImpl]
                include(each.as_posix())
        return ""

    def proc(self, argv: list[str], start: int, end: int):
        for each_dir in process_nest(self.ctx, start, end).strip().splitlines():
            each_dir = each_dir.strip()
            if not each_dir:
                continue
            directory = Path(each_dir)
            for file in directory.iterdir():
                if file.is_file() and file.suffix == '.op':
                    include = self.ctx.storage[names.NAME_IncludeImpl]
                    include(file.as_posix())
        return ""
