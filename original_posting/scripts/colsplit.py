from __future__ import annotations
from concurrent.futures import process
from original_posting.types import CommandEntry, Context
from original_posting.parsing import process_nest
import bs4

_html_factory = bs4.BeautifulSoup("", "html.parser")

class ColSplit(CommandEntry):
    _inc = 0
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, argv: list[str], start: int, end: int):
        split_indices = []
        starts = [start]
        while True:
            split_index = self.ctx.source.find("@split", start, end)
            if split_index == -1:
                break
            split_indices.append((start, split_index))
            start = split_index + len("@split")
        split_indices.append((start, end))
        xs = []
        for start, end in split_indices:
            x = process_nest(self.ctx, start, end)
            xs.append(x)
        contents = '\n'.join(rf"<td colsplit>{x}</td>" for x in xs)
        return rf'<table> <tr colsplit> {contents} </tr> </table>'

    def inline_proc(self, start: int, end: int):
        raise ValueError("inline @if is invalid")
