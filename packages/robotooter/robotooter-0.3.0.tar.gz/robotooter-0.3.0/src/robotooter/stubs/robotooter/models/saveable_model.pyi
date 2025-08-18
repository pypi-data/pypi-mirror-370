from pathlib import Path
from typing import Self

from pydantic import BaseModel

class SaveableModel(BaseModel):
    filename: Path | None
    @classmethod
    def load(cls, filename: Path) -> Self: ...
    def save(self) -> None: ...
