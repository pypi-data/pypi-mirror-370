from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel


class RtMedia(BaseModel):
    id: str | None = None
    file_path: Path
    description: str | None = None

class StatusVisibility(StrEnum):
    Direct = 'direct' # post will be visible only to mentioned users, known in Mastodon’s UI as “Mentioned users only”
    Private = 'private' # post will be visible only to followers, known in Mastodon’s UI as “Followers only”
    Unlisted = 'unlisted' # post will be public but will not appear on the public timelines
    Public = 'public'
    # https://mastodonpy.readthedocs.io/en/stable/05_statuses.html#mastodon.Mastodon.status_post

class RtStatus(BaseModel):
    id: str| None = None
    text: str = ''
    in_reply_to_id: str | None = None
    url: str| None = None
    media: list[RtMedia] = []
    spoiler_text: str | None = None
    quote_id: str | None = None
    visibility: str | None = None
