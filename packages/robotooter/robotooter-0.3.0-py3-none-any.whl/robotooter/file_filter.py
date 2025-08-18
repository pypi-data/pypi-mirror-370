from io import TextIOWrapper
from pathlib import Path
from typing import IO, Any, Iterable, Sequence

from robotooter.filters.base_filter import BaseFilter

FileOrPath = str | Path | IO[Any]

class FileFilter:
    def __init__(self, filters: list[BaseFilter]|None = None):
        self.filters = filters or []

    def process_files(self, input_files: Sequence[FileOrPath], output_path_or_file: FileOrPath)-> None:
        output_file, output_opened = self._open(output_path_or_file, 'w')
        try:
            for file in input_files:
                self.process_file(file, output_file)
        except Exception as e:
            print(e)
            raise e
        finally:
            if output_opened and output_file:
                output_file.close()

    def process_file(self, input_path_or_file: FileOrPath, output_path_or_file: FileOrPath | None) -> None:
        input_file, input_opened  = self._open(input_path_or_file)
        if input_file is None:
            raise FileNotFoundError("Can't read None, yo")
        output_file, output_opened = self._open(output_path_or_file, 'w')
        [f.reset() for f in self.filters]

        try:
            for line in self.filter_lines(input_file):
                if output_file:
                    output_file.write(line)
        except Exception as e:
            print(e)
            raise e
        finally:
            if input_opened:
                input_file.close()
            if output_opened and output_file:
                output_file.close()

    def filter_lines(self, lines: Iterable[str]) -> Iterable[str]:
        for line in lines:
            for f in self.filters:
                result = f.process(line)
                if result is None:
                    break  # Drop line
                line = result  # Pass updated line to next filter
            else:
                yield line  # Yield only if not dropped by any filter

    def _open(self, file_or_path: FileOrPath | None, mode:str='r') -> tuple[IO|None, bool]:
        if file_or_path is None:
            return None, False

        if isinstance(file_or_path, TextIOWrapper):
            return file_or_path, False

        return open(str(file_or_path), mode), True
