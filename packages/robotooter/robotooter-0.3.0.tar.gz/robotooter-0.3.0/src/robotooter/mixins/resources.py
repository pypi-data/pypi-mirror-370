import re
import shutil
from importlib import resources as resources
from pathlib import Path
from typing import Protocol

RE_BOTLESS = re.compile('Bot$')
RE_MODNAME = re.compile(r'(?<!^)(?=[A-Z])')


class HasWorkingDirectory(Protocol):
    working_directory: Path

    def pkg_resources_path(self) -> Path: ...

    def resource_path(self, sub_path: str | None = None) -> Path: ...

class ResourcesMixin:
    def pkg_resources_path(self) -> Path:
        botless = RE_BOTLESS.sub('', self.__class__.__name__)
        mod_name = RE_MODNAME.sub('_', botless).lower()
        return Path(str(resources.files(f"{mod_name}"))) / "resources"

    def install_package_resources(self: HasWorkingDirectory) -> None:
        shutil.copytree(self.pkg_resources_path(), self.resource_path())

    def resource_path(self: HasWorkingDirectory, sub_path: str | None = None) -> Path:
        p = self.working_directory / "resources"
        if sub_path is not None:
            return p / sub_path
        return p
