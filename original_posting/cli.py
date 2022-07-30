from original_posting import process, Runtime
from pathlib import Path
import wisepy2
import pathlib
import typing
import warnings
import sys

def _batch_compile_impl(file: Path, out: Path, force: bool, suffix: str):
    if file.is_dir():
        for each in file.iterdir():
            _batch_compile_impl(each, out / each.name, force, suffix)
    else:
        outfile = out.with_suffix(suffix)
        outfile.parent.mkdir(0o777, parents=True, exist_ok=True)
        result = process(str(file))
        if outfile.exists() and not force:
            warnings.warn("{} already exists. Skipped. Add --force to perform the inplace operation.".format(str(outfile)))
            return
        with outfile.open('w', encoding='utf-8') as f:
            f.write(result)

def command(filename: str, *, out: str = "", extra_search_path: str = "", force: bool = False, batch: bool = False, suffix: str = ".html"):
    """
    filename : input file name.
    out      : output file name.
    force    : if set, overwrite the output file if it exists.
    batch    : compile a directory recursively.
    suffix   : if --batch is given, the suffix of the output file. default is ".html".

    e.g.,
    op a.op --out a.html --force
    op src/ --out dst/ --force --batch --suffix .html
    """
    sys.argv.clear()
    if extra_search_path:
        Runtime.search_path.extend(filter(None, extra_search_path.split(';')))
    if batch:
        assert out, "--out is required when --batch is given."
        directory = Path(filename)
        assert directory.is_dir(), "--batch requires a directory as input."
        _batch_compile_impl(directory, Path(out), force, suffix)
        return

    if not out:
        out = str(pathlib.Path(filename).with_suffix(".html"))

    result = process(filename)
    if pathlib.Path(out).exists() and not force:
        warnings.warn("{} already exists. Skipped. Add --force to perform the inplace operation.".format(out))
        return

    with open(out, 'w', encoding='utf-8') as f:
        f.write(result)

command.__annotations__ = typing.get_type_hints(command)

def main():
    wisepy2.wise(command)() # type: ignore

