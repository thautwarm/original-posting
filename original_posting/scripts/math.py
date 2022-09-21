from original_posting.types import CommandEntry, Context
from original_posting.parsing import process_nest
from multiprocessing.pool import ThreadPool
import javascript
import time

pool = ThreadPool(processes=1)

last_result = None


mn = javascript.require("mathjax-node")
mn.config({"MathJax": {}})


def mathjax2html(code, use_svg=True):
    last_result = None

    def set_result(x):
        nonlocal last_result
        last_result = x
        return x

    def get_result():
        return last_result

    h = use_svg and "svg" or "html"
    mn.typeset(
        {
            "math": code,
            "format": "TeX",
            h: True,
        },
        lambda data, *args: set_result(data[h]),
    )

    while True:
        time.sleep(0.03)
        if get_result() is not None:
            return get_result()


class Mathjax(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, args: list[str], _start: int, _stop: int) -> str:
        code = process_nest(self.ctx, _start, _stop)
        coro = pool.apply_async(mathjax2html, [code, not ("html" in args)])
        res = coro.get()
        assert isinstance(res, str)
        return res
