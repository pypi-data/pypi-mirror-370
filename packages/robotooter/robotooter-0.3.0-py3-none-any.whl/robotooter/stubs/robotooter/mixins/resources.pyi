from pathlib import Path
from typing import Protocol

from _typeshed import Incomplete

RE_BOTLESS: Incomplete
RE_MODNAME: Incomplete

class HasWorkingDirectory(Protocol):
    working_directory: Path
    def pkg_resources_path(self) -> Path: ...
    def resource_path(self, sub_path: str | None = None) -> Path: ...

class ResourcesMixin:
    def pkg_resources_path(self) -> Path: ...
    def install_package_resources(self) -> None: ...
    def resource_path(self, sub_path: str | None = None) -> Path: ...
