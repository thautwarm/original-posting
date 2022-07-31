from __future__ import annotations
from original_posting.build import Build, BuildOptions
from original_posting.types import Runtime
import wisepy2
import os


def command(
    entry: str,
    *,
    project_path: str = "",
    out: str = "out",
    extra_search_path: str = "",
    force: bool = False,
    suffix: str = ".html",
):
    """
    entry        : input file name.
    out          : output file name.
    force        : if set, overwrite the output file if it exists.
    suffix       : if --batch is given, the suffix of the output file. default is ".html".
    extra_search_path : extra search directories providing the commands, separated by ';'.
    e.g.,
    op a.op --out a.html --force
    op src/ --out dst/ --force --batch --suffix .html
    """
    Runtime.search_path.extend(filter(None, extra_search_path.split(";")))
    opts = BuildOptions(force, suffix, out)
    if not project_path:
        project_path = os.path.dirname(os.path.abspath(entry))
    build = Build(project_path, [entry], opts)
    build.build_all()
    return

def main():
    wisepy2.wise(command)()  # type: ignore
