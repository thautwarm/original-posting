from original_posting.types import CommandEntry, Context, OPDocument
from original_posting.parsing import process_nest
import latex2mathml.converter

class Mathjax(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

        callbacks = self.ctx.target_doc.callbacks
        if self.add_mathjax not in callbacks:
            callbacks.append(self.add_mathjax)

    @staticmethod
    def add_mathjax(doc: OPDocument):
        doc.code += r"""
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script type="text/javascript" id="MathJax-script" async
            src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/mml-chtml.js">
        </script>
        """

    def proc(self, args: list[str], _start: int, _stop: int) -> str:
        code = process_nest(self.ctx, _start, _stop)
        return latex2mathml.converter.convert(code)
