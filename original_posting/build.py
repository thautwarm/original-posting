from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from original_posting.parsing import process
from original_posting.utils import get_relative_path
from original_posting.types import OPDocument
import original_posting.builtin_names as names
import pathlib
import typing
import warnings
import os


@dataclass
class BuildOptions:
    force: bool
    suffix: str
    outdir: str


class Build:
    def __init__(
        self,
        project_path: str | pathlib.Path,
        files_to_build: typing.Sequence[str],
        opts: BuildOptions,
    ):
        self.files_to_build: deque[OPDocument] = deque()
        self.processed_files: set[str] = set()
        self.built_docs: dict[str, OPDocument] = {}
        if not isinstance(project_path, pathlib.Path):
            project_path = pathlib.Path(project_path).absolute()
        self.project_path = project_path
        self.storage: dict[str, typing.Any] = {names.NAME_Rootdir: str(project_path)}
        self.options = opts

        for file in files_to_build:
            self._include(pathlib.Path(file).absolute())

    def build_all(self):
        while self._handle_one():
            pass

        self._performance_global_callbacks()
        self._dump_to_disk()

    def _include(self, file_to_include: pathlib.Path):
        """
        file_to_include: the absolute path of the file to include
        """
        assert file_to_include.is_absolute()
        proj_based_path = get_relative_path(file_to_include, self.project_path)

        if proj_based_path in self.processed_files:
            return
        self.processed_files.add(proj_based_path)

        outfile = (
            pathlib.Path(
                os.path.join(self.project_path, self.options.outdir, proj_based_path)
            )
            .with_suffix(self.options.suffix)
            .absolute()
        )
        wd = file_to_include.absolute().parent
        op_doc = OPDocument(
            project_based_path=proj_based_path,
            project_path_absolute=self.project_path,
            source_path_absolute=file_to_include,
            working_dir_absolute=wd,
            output_path_absolute=outfile,
            project_docs=self.built_docs,
        )
        self.files_to_build.append(op_doc)

    def _handle_one(self):
        if not self.files_to_build:
            return False

        immature_doc = self.files_to_build.popleft()

        # directory =

        def include_impl(file_to_build: str):
            self._include(immature_doc.working_dir_absolute / file_to_build)

        self.storage[names.NAME_IncludeImpl] = include_impl

        with immature_doc.source_path_absolute.open("r", encoding="utf-8") as f:
            src_code = f.read()

        result = process(
            filename=str(immature_doc.source_path_absolute),
            source=src_code,
            storage=self.storage,
            target_doc=immature_doc,
        )
        immature_doc.code = result
        self.built_docs[immature_doc.project_based_path] = immature_doc
        return True

    def _performance_global_callbacks(self):
        for each in reversed(self.built_docs.values()):
            for my_callback in each.callbacks:
                my_callback(each)

    def _dump_to_disk(self):
        for doc in self.built_docs.values():
            outfile = doc.output_path_absolute
            outfile.parent.mkdir(0o777, parents=True, exist_ok=True)
            if outfile.exists() and not self.options.force:
                warnings.warn(
                    "{} already exists. Skipped. Add --force to perform the inplace operation.".format(
                        str(outfile)
                    )
                )
                return

            with outfile.open("w", encoding="utf-8") as f:
                f.write(doc.code)

            print(f"Dumped {outfile}.")
