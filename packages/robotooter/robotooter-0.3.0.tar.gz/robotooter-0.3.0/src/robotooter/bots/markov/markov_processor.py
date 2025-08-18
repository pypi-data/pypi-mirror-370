import glob
import os
import sys
from pathlib import Path

import markovify

from robotooter.file_filter import FileFilter
from robotooter.filters.base_filter import BaseFilter

DEFAULT_STATE_SIZE = 3

class MarkovProcessor:
    def __init__(self, working_directory: Path, filters: list[BaseFilter]):
        self.filters = filters
        self.working_directory = working_directory
        self.data_dir = working_directory / "data"

        self.source_dir = self.data_dir / "sources"
        self.consolidated_file_path = self.data_dir / "consolidated.txt"
        self.model_path = self.data_dir / "model.json"
        self._model: markovify.Text | None = None

    def preprocess_sources(self) -> None:
        input_files = glob.glob(os.path.join(self.source_dir, "*.txt"))
        if not input_files:
            print("No input files found. Cowardly refusing to go on.")
            sys.exit(1)

        input_files.sort()

        processor = FileFilter(filters=self.filters)
        processor.process_files(input_files, self.consolidated_file_path)

    def build_model(self, state_size: int = DEFAULT_STATE_SIZE) -> None:
        if not os.path.exists(self.consolidated_file_path):
            raise Exception("Consolidated file not found. Cowardly refusing to go on.")

        all_data = open(self.consolidated_file_path, "r").read()
        text_model = markovify.Text(all_data, state_size=state_size)

        with open(self.model_path, "w") as model_file:
            model_file.write(text_model.to_json())

    @property
    def consolidated_exists(self) -> bool:
        return os.path.exists(self.consolidated_file_path)

    @property
    def model_exists(self) -> bool:
        return os.path.exists(self.model_path)
