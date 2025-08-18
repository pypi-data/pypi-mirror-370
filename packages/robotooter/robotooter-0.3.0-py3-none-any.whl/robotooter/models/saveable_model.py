from pathlib import Path
from typing import Self

from pydantic import BaseModel, Field


class SaveableModel(BaseModel):
    filename: Path | None = Field(exclude=True, default=None)

    @classmethod
    def load(cls, filename: Path) -> Self:
        data = filename.read_text()
        instance = cls.model_validate_json(data)
        instance.filename = filename
        return instance

    def save(self) -> None:
        if self.filename:
            self.filename.write_text(self.model_dump_json(indent=2))
