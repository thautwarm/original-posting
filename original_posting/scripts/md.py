from original_posting.types import CommandEntry, Context, OPDocument
from original_posting.parsing import process_nest
import markdown
import warnings

class Md2Html(CommandEntry):
    def __init__(self, ctx: Context):
        self.ctx = ctx
        if self.callback not in self.ctx.target_doc.callbacks:
            self.ctx.target_doc.callbacks.append(self.callback)

    @staticmethod
    def callback(cur_doc: OPDocument):
        try:
            import bs4
        except ImportError:
            warnings.warn("installing beautifulsoup4 to automatically setting titles for markdown documents")
            return

        for doc in cur_doc.project_docs.values():
            if not doc.title:
                h1 = bs4.BeautifulSoup(doc.code, 'html.parser').find("h1")
                if h1:
                    doc.title = h1.text


    def proc(self, argv: list[str], _start: int, _stop: int) -> str:
        return markdown.markdown(process_nest(self.ctx, _start, _stop), extensions=argv)
