from pathlib import Path
from typing import Any

from robotooter.models.statuses import RtMedia as RtMedia
from robotooter.models.statuses import RtStatus as RtStatus
from robotooter.models.statuses import StatusVisibility as StatusVisibility

class FakeClient:
    status_calls: list[dict[str, Any]]
    media_calls: list[str]
    login_calls: list[list[str]]
    auth_url_call_count: int
    def __init__(self, output_path: Path) -> None: ...
    def status_post(self,
        status: str,
        in_reply_to_id: str | None = None,
        media_ids: list[str] | None = None,
        spoiler_text: str | None = None,
        quote_id: str | None = None,
        visibility: StatusVisibility | None = None
    ) -> RtStatus: ...
    def media_post(self, media_file: str, description: str) -> RtMedia: ...
    def get_auth_url(self) -> str: ...
    def log_in(self, code: str, to_file: str) -> None: ...
