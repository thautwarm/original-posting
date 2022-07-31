"""
'toc' command generates a table of contents for the given file.
@begin toc --depth 2
Table of contents
@end toc
"""
from ast import USub
from original_posting import CommandEntry, Context, process_nest
import bs4
import wisepy2
import typing
import uuid
import shlex


class Arguments(typing.NamedTuple):
    depth: int


def parse_args(*, depth: int = 2):
    return Arguments(depth=depth)


def generate_toc(
    depth: int,
    max_depth: int,
    nodes: list[bs4.Tag],
    doc: bs4.BeautifulSoup,
) -> bs4.Tag:
    tag_name = f"h{depth}"
    ul = doc.new_tag("ul")

    def add_sub(n: bs4.Tag):
        title = n.text
        address = str(uuid.uuid4())
        n.insert(0, doc.new_tag("div", id=address))
        li = doc.new_tag("li")
        a = doc.new_tag("a", href="#" + address)
        a.append(title)
        li.append(a)
        if depth <= max_depth:
            parent = n.parent
            assert parent
            i = parent.index(n) + 1
            parent_contents = parent.contents
            next_level_nodes = []
            while i < len(parent_contents):
                sibling = parent_contents[i]
                if isinstance(sibling, bs4.Tag):
                    if sibling.name == tag_name:
                        break
                    next_level_nodes.append(sibling)
                i += 1
            li.append(generate_toc(depth + 1, max_depth, next_level_nodes, doc))
        ul.append(li)

    for node in nodes:
        if not isinstance(node, bs4.Tag):
            continue

        if isinstance(node, bs4.Tag) and node.name == tag_name:
            add_sub(node)

        for n in node.find_all(tag_name):
            add_sub(n)

    return ul


class Replacer:
    def __init__(self, uuid: str, depth: int):
        self.uuid = uuid
        self.depth = depth

    def __call__(self, source: str):
        doc = bs4.BeautifulSoup(source, "html.parser")
        toc = doc.find("div", {"class": "toc", "refid": self.uuid})
        if not toc:
            return source
        inner = generate_toc(1, self.depth, [doc], doc)
        toc.append(inner)
        return str(doc)


class TocEntry(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, argv: list[str], _start: int, _stop: int) -> str:
        args = wisepy2.wise(parse_args)(argv)
        ref_id = str(uuid.uuid4())
        callbacks = self.ctx.storage.setdefault("markdown-postprocessing", [])
        callbacks.append(Replacer(ref_id, args.depth))
        return f'<div class="toc" refid="{ref_id}"></div>'

    def inline_proc(self, _start: int, _end: int) -> str:
        return self.proc(
            shlex.split(process_nest(self.ctx, _start, _end).strip()), _start, _end
        )
