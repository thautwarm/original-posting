from posixpath import split
from original_posting import process, Runtime
import wisepy2
import pathlib
import typing
import warnings

def command(filename: str, *, out: str = "", extra_search_path: str = "", force: bool = False):
    """
    filename : input file name
    out      : output file name
    force    : if set, overwrite the output file if it exists.

    e.g.,
    op a.op --out a.html --force
    """
    if extra_search_path:
        Runtime.search_path.extend(filter(None, extra_search_path.split(';')))
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

