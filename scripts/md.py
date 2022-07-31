from original_posting import CommandEntry, Context, process_nest
import markdown2


class Md2Html(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, args: list[str], _start: int, _stop: int) -> str:
        callbacks = self.ctx.storage.setdefault("markdown-postprocessing", [])
        html = markdown2.markdown(process_nest(self.ctx, _start, _stop))
        for f in callbacks:
            html = f(html)
        return html
