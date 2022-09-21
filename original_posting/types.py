from __future__ import annotations
from dataclasses import dataclass, field
import pathlib
import typing
import abc

DEFAULT_SCRIPT_PATH = "~/.original-posting"
DEFAULT_SCRIPT_PATH_INTERNAL = pathlib.Path(__file__).parent.joinpath("scripts").as_posix()

@dataclass
class OPDocument:
    """
    When building the doc, the following variables are available:
    - `doc_tags`: a dict of tags and their values.
    - `doc_data`: a dict for storing the document specific data.
    - `project_based_path`: the path of the document relative to the project root.
    - `project_docs`: a dict mapping all `project_based_path`s to `OPDocument`s in this project.
    - `callbacks`: a list of callbacks to be called after the document is built.
    - `source_path_absolute`: the absolute path of the source file.
    - `output_path_absolute`: the absolute path of the output file.
    - `working_dir_absolute`: the absolute path of the source file's directory.
    - `project_path_absolute`: the absolute path of the project root.
    - `title`: the title of the document.

    Before performing the callback, `code` is always an empty string.
    """

    project_based_path: str
    project_path_absolute: pathlib.Path
    source_path_absolute: pathlib.Path
    working_dir_absolute: pathlib.Path
    output_path_absolute: pathlib.Path
    project_docs: typing.Dict[str, OPDocument]
    callbacks: list[typing.Callable[[OPDocument], None]] = field(default_factory=list)
    tags: list[object] = field(default_factory=list)
    data: dict = field(default_factory=dict)
    code: str = ""
    title: str = ""

    def __repr__(self) -> str:

        return f'<OPDocuement {self.project_based_path} in {self.project_path_absolute}>'

@dataclass
class Scope:
    name: str
    cmd_entry: CommandEntry
    start: int
    args: list[str]
    start_line: int
    start_col: int


class CommandEntry(abc.ABC):
    @abc.abstractmethod
    def __init__(self, ctx: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def proc(self, argv: list[str], start: int, end: int):
        raise NotImplementedError

    def inline_proc(self, start: int, end: int):
        return self.proc([], start, end)


@dataclass
class Context:
    source: str
    n_source: int
    pos: int
    line: int
    col: int
    cur_scope: Scope | None
    os: str  # which os the source is written
    linesep: str
    file: str
    storage: dict  # application storage
    target_doc: OPDocument


if typing.TYPE_CHECKING:

    class Operator(typing.Protocol):
        def __call__(self, ctx: Context, __start: int, __stop: int) -> str:
            ...

else:
    Operator = object


def _default_op(ctx: Context, _start: int, _stop: int) -> str:
    return ctx.source[_start:_stop]


class Runtime:
    search_path: list[str] = [DEFAULT_SCRIPT_PATH, DEFAULT_SCRIPT_PATH_INTERNAL]
    operators: dict[typing.Literal["[]", "()", "{}"], Operator] = {
        "[]": _default_op,
        "{}": _default_op,
        "()": _default_op,
    }


__all__ = ['OPDocument', 'Runtime', 'Operator', 'Context', 'CommandEntry']