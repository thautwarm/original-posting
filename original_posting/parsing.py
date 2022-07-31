from __future__ import annotations
from original_posting.types import OPDocument, CommandEntry, Scope, Context, Runtime
from original_posting.utils import create_syntax_error, load_from_source
from pathlib import Path
import os
import io
import re
import shlex
import typing


_line_end = re.compile("\n\r|\n|\r|$")
_inline_command_head = re.compile(r"[^ \r\n\t\|]+\|")


_GLOBAL_STORAGE = {"builtin-rootdir": os.getcwd()}


def new_context(filename: str, source: str, storage: dict, target_doc: OPDocument):
    return Context(
        source,
        len(source),
        pos=0,
        line=0,
        col=0,
        cur_scope=None,
        os="unknown",
        linesep=os.linesep,
        file=filename,
        storage=storage,
        target_doc=target_doc,
    )


def new_context_from_existing(
    ctx: Context,
    start: int,
    end: int,
    start_line: int,
    start_col: int,
):
    return Context(
        ctx.source,
        end,
        pos=start,
        line=start_line,
        col=start_col,
        cur_scope=None,
        os=ctx.os,
        linesep=ctx.linesep,
        file=ctx.file,
        storage=ctx.storage,
        target_doc=ctx.target_doc,
    )


if typing.TYPE_CHECKING:
    NotFound = None
    Span = tuple[int, int]
    EndPos = int
    SearchMatch = None | tuple[Span, EndPos]


def find_match(
    l: str, r: str, escapes: frozenset[str], s: str, offset: int, endpos: int
) -> SearchMatch:
    if not s.startswith(l, offset):
        return None
    offset += len(l)
    start = offset
    while offset < endpos:
        for escape in escapes:
            if s.startswith(escape, offset):
                offset += len(escape)
                break
        else:
            if s.startswith(r, offset):
                return (start, offset), offset + len(r)
            offset += 1


_cmd_modules: dict[str, typing.Type[CommandEntry]] = {}


def get_command_entry(cmd_name: str):
    if cmd_name in _cmd_modules:
        return _cmd_modules[cmd_name]  # type: ignore

    cmd_file_abs_path = find_file(cmd_name + ".py")
    if not cmd_file_abs_path:
        return
    m = load_from_source(cmd_file_abs_path)
    for v in m.__dict__.values():
        if (
            isinstance(v, type)
            and v is not CommandEntry
            and issubclass(v, CommandEntry)
        ):
            _cmd_modules[cmd_name] = v
            return v


def find_file(filename: str) -> str | None:
    for each in Runtime.search_path:
        search_dir = Path(each).expanduser()
        if not search_dir.exists():
            continue
        for p in search_dir.iterdir():
            if p.name == filename:
                return str(p.absolute())


def _new_scope(ctx: Context, i: int):
    orig_i = i
    i += len("@begin")
    ctx.col += len("@begin")

    find = _line_end.search(ctx.source, i, ctx.n_source)
    if not find:
        raise create_syntax_error(
            "@begin not found", ctx.source[orig_i:], ctx.line, i, ctx.file
        )

    i_line_end, i_next = find.span()

    cmd = ctx.source[i:i_line_end].strip()
    args = shlex.split(cmd)
    if not args:
        raise create_syntax_error(
            msg=f"{ctx.source[i:i_line_end]} is not a valid scope name",
            text=ctx.source[orig_i:i_line_end],
            line=ctx.line,
            offset=i,
            file=ctx.file,
        )
    cmd, *args = args
    cmd_entry = get_command_entry(cmd)
    if not cmd_entry:
        raise create_syntax_error(
            f"command {cmd} is not found",
            text=ctx.source[orig_i:i_line_end],
            line=ctx.line,
            offset=i,
            file=ctx.file,
        )
    ctx.pos = i_next
    ctx.line += 1
    ctx.col = 0
    ctx.cur_scope = Scope(cmd, cmd_entry(ctx), i_next, args, ctx.line, ctx.col)
    return


def _new_scope_inline(builder: io.StringIO, ctx: Context, i: int):
    m = _inline_command_head.match(ctx.source, i + 1, ctx.n_source)
    if not m:
        return False
    _, command_name_end = m.span()
    command_name_end -= 1
    cmd = ctx.source[i + 1 : command_name_end]
    n_xor_sign = 0
    xor_sign_i = command_name_end
    while xor_sign_i < ctx.n_source and ctx.source[xor_sign_i] == "|":
        n_xor_sign += 1
        xor_sign_i += 1
    pat = "|" * n_xor_sign
    command_content_start = xor_sign_i
    command_content_end = ctx.source.find(pat, command_content_start, ctx.n_source)
    if command_content_end < 0:
        raise create_syntax_error(
            msg=f"{cmd} starts with {n_xor_sign} '|' sign, but no matching ending was found.",
            text=ctx.source[i : command_content_start + 10],
            line=ctx.line,
            offset=i,
            file=ctx.file,
        )
    cmd_entry = get_command_entry(cmd)
    if not cmd_entry:
        raise create_syntax_error(
            f"command {cmd} is not found",
            text=ctx.source[i : command_content_start + 10],
            line=ctx.line,
            offset=i,
            file=ctx.file,
        )
    i_next = command_content_end + n_xor_sign
    ctx.pos = i_next
    scope = ctx.cur_scope = Scope(cmd, cmd_entry(ctx), i_next, [], ctx.line, ctx.col)
    try:
        text = scope.cmd_entry.inline_proc(command_content_start, i_next - n_xor_sign)
    except Exception as e:
        raise create_syntax_error(
            f"{cmd} failed to process (args: {[]})",
            text=ctx.source[i : i_next + 20],
            line=ctx.line,
            offset=i,
            file=ctx.file,
        ) from e
    finally:
        ctx.cur_scope = None
    builder.write(text)
    l_inc = ctx.source.count(ctx.linesep, i, i_next)
    if l_inc:
        ctx.line += l_inc
        ctx.col = 0
    else:
        ctx.col = i_next

    return True


def _end_scope(builder: io.StringIO, ctx: Context, i: int):
    o_orig = i
    i += len("@end")
    find = _line_end.search(ctx.source, i)
    if not find:
        return False
    i_line_end, i_next = find.span()
    cmd = ctx.source[i:i_line_end].strip()
    cur_scope = ctx.cur_scope
    assert cur_scope
    if not cmd.strip():
        raise create_syntax_error(
            f"'@end' followed by no command name, did you mean by '@end {cur_scope.name}'?",
            text=ctx.source[o_orig:i_line_end],
            line=ctx.line,
            offset=i,
            file=ctx.file,
        )
    if cmd != cur_scope.name:
        return False
    try:
        text = cur_scope.cmd_entry.proc(cur_scope.args, cur_scope.start, o_orig)
    except Exception as e:
        raise create_syntax_error(
            f"{cur_scope.name} failed to process (args: {cur_scope.args})",
            text=ctx.source[o_orig:i_line_end],
            line=ctx.line,
            offset=i,
            file=ctx.file,
        ) from e
    builder.write(text)
    ctx.pos = i_next
    ctx.line += 1
    ctx.col = 0
    return True


_parens_escape = frozenset({r"\(", r"\)"})
_brackets_escape = frozenset({r"\[", r"\]"})
_braces_escape = frozenset({r"\{", r"\}"})
_escapes = {
    "[]": _brackets_escape,
    "()": _parens_escape,
    "{}": _braces_escape,
}


def _handle_operator(builder: io.StringIO, ctx: Context, i: int):
    for l, r, op in ("(", ")", "()"), ("[", "]", "[]"), ("{", "}", "{}"):
        found = find_match(l, r, _escapes[op], ctx.source, i + 1, ctx.n_source)
        if found:
            (start, end), ctx.pos = found
            l_inc = str.count(ctx.source, ctx.linesep, start, end)
            if l_inc:
                raise create_syntax_error(
                    "unexpected newline", ctx.source[i : end + 1], ctx.line, i, ctx.file
                )
            ctx.col += 1
            builder.write(Runtime.operators[op](ctx, start, end))
            ctx.col = end + 1
            return True
    return False


def process_iter(builder: io.StringIO, ctx: Context):
    i = ctx.pos
    while ctx.source.startswith("\\@", i):
        i += len("\\@")
    ctx.pos = i
    if i >= ctx.n_source:
        return False

    if ctx.cur_scope:
        if ctx.source.startswith("@end", i) and _end_scope(builder, ctx, i):
            ctx.cur_scope = None
            return True
        c = ctx.source[i]

        if c in ctx.linesep:
            ctx.line += 1
            ctx.col = 0
        else:
            ctx.col += 1
        ctx.pos = i + 1
        return True

    if ctx.source.startswith("@begin", i):
        _new_scope(ctx, i)
        ctx.line += 1
        ctx.col = 0
        return True
    elif ctx.source.startswith("@", i):
        # operators
        if _handle_operator(builder, ctx, i):
            return True
        # inline commands
        if _new_scope_inline(builder, ctx, i):
            return True

    c = ctx.source[i]
    builder.write(c)
    if c in ctx.linesep:
        ctx.line += 1
        ctx.col = 0
    else:
        ctx.col += 1
    ctx.pos = i + 1
    return True


def process(filename: str, source: str, storage: dict, target_doc: OPDocument):
    storage = storage or _GLOBAL_STORAGE
    ctx = new_context(filename, source, storage, target_doc)
    buf = io.StringIO()
    while process_iter(buf, ctx):
        pass
    return buf.getvalue()


def process_nest(ctx: Context, start: int, end: int):
    assert ctx.cur_scope
    cur_scope = ctx.cur_scope
    new_ctx = new_context_from_existing(
        ctx,
        start,
        end,
        cur_scope.start_line,
        cur_scope.start_col,
    )
    buf = io.StringIO()
    while process_iter(buf, new_ctx):
        pass
    return buf.getvalue()


__all__ = [
    "process",
    "process_nest",
    "Runtime",
    "create_syntax_error",
]
