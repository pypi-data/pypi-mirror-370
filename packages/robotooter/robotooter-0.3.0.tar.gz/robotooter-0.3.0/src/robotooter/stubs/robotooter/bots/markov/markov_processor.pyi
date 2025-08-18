from pathlib import Path

from _typeshed import Incomplete

from robotooter.file_filter import FileFilter as FileFilter
from robotooter.filters.base_filter import BaseFilter as BaseFilter

DEFAULT_STATE_SIZE: int

class MarkovProcessor:
    filters: Incomplete
    working_directory: Incomplete
    data_dir: Incomplete
    source_dir: Incomplete
    consolidated_file_path: Incomplete
    model_path: Incomplete
    def __init__(self, working_directory: Path, filters: list[BaseFilter]) -> None: ...
    def preprocess_sources(self) -> None: ...
    def build_model(self, state_size: int = ...) -> None: ...
    @property
    def consolidated_exists(self) -> bool: ...
    @property
    def model_exists(self) -> bool: ...
