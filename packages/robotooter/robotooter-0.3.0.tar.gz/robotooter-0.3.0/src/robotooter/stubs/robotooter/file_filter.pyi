from pathlib import Path
from typing import IO, Any, Iterable, Sequence

from _typeshed import Incomplete

from robotooter.filters.base_filter import BaseFilter as BaseFilter

FileOrPath = str | Path | IO[Any]

class FileFilter:
    filters: Incomplete
    def __init__(self, filters: list[BaseFilter] | None = None) -> None: ...
    def process_files(self, input_files: Sequence[FileOrPath], output_path_or_file: FileOrPath) -> None: ...
    def process_file(self, input_path_or_file: FileOrPath, output_path_or_file: FileOrPath | None) -> None: ...
    def filter_lines(self, lines: Iterable[str]) -> Iterable[str]: ...
