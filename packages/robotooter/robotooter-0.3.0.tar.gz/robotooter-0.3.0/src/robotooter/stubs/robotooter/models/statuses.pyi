from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel

class RtMedia(BaseModel):
    id: str | None
    file_path: Path
    description: str | None

class StatusVisibility(StrEnum):
    Direct = 'direct'
    Private = 'private'
    Unlisted = 'unlisted'
    Public = 'public'

class RtStatus(BaseModel):
    id: str | None
    text: str
    in_reply_to_id: str | None
    url: str | None
    media: list[RtMedia]
    spoiler_text: str | None
    quote_id: str | None
    visibility: str | None
