from __future__ import annotations
from original_posting.types import CommandEntry, Context, OPDocument
from original_posting.parsing import process_nest
import bs4
import wisepy2
import yaml
import io
import shutil

def parse_args(id: str):
    return id

_html_factory = bs4.BeautifulSoup("", "html.parser")


def AddImage(op: OPDocument):
    images: set[str] = op.data.setdefault((ImageAdderEntry, "path"), set())
    for image_path in images:
        src_path = op.source_path_absolute.parent.joinpath(image_path)
        dest_path = op.output_path_absolute.parent.joinpath(image_path)
        dest_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        try:
            shutil.copy(str(src_path), str(dest_path), follow_symlinks=True)
        except shutil.SameFileError:
            pass

class ImageAdderEntry(CommandEntry):
    _inc = 0
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def proc(self, argv: list[str], start: int, end: int):
        identity = wisepy2.wise(parse_args)(argv)
        source = process_nest(self.ctx, start, end)
        configs = yaml.load(io.StringIO(source), yaml.loader.SafeLoader)
        if isinstance(configs, dict) and 'src' in configs:
            imagepath = str(configs["src"])
            image_paths: set[str] = self.ctx.target_doc.data.setdefault((ImageAdderEntry, "path"), set())
            image_paths.add(imagepath)
            width = configs.get("width", "1200px")
            img_float = configs.get("float", "")
            images: dict[str, bs4.Tag] = self.ctx.target_doc.data.setdefault(ImageAdderEntry, {})
            tag_image = _html_factory.new_tag("image")
            tag_image.attrs["width"] = width
            tag_image.attrs["src"] = imagepath
            if img_float:
                tag_div = _html_factory.new_tag("div")
                tag_div.attrs["style"] = "width: {}; float: {}; display: inline-block;".format(width, img_float)
                tag_div.contents.append(tag_image)
                images[identity] = tag_div
            else:
                images[identity] = tag_image
        else:
            raise ValueError("Invalid '@begin img' block")
        if AddImage not in self.ctx.target_doc.callbacks:
            self.ctx.target_doc.callbacks.append(AddImage)
        return ''

    def inline_proc(self, start: int, end: int):
        id = process_nest(self.ctx, start, end).strip()
        images: dict[str, bs4.Tag] = self.ctx.target_doc.data.setdefault(ImageAdderEntry, {})
        if id in images:
            return str(images[id])
        raise ValueError("Image not found: {}".format(id))
