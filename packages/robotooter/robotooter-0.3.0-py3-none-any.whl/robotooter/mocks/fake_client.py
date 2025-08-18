from pathlib import Path
from typing import Any

from robotooter.models.statuses import RtMedia, RtStatus, StatusVisibility


class FakeClient:
    def __init__(self, output_path: Path):
        self.status_calls: list[dict[str, Any]] = []
        self.media_calls: list[str] = []
        self._output_path = output_path
        self.login_calls: list[list[str]] = []
        self.auth_url_call_count = 0

    def status_post(
            self,
            status: str,
            in_reply_to_id: str | None = None,
            media_ids: list[str]|None = None,
            spoiler_text: str|None=None,
            quote_id: str|None=None,
            visibility: StatusVisibility|None=None
    ) -> RtStatus:
        current_call_id = len(self.status_calls) + 1
        self.status_calls.append({
            'status': status,
            'in_reply_to_id':in_reply_to_id,
            'media_ids':media_ids,
            'spoiler_text': spoiler_text,
            'quote_id': quote_id,
            'visibility': visibility,
            'id': current_call_id,
        })
        output_path = self._output_path / f"{current_call_id}.txt"
        with output_path.open("w", encoding="utf-8") as f:
            f.write(f"in_reply_to_id: {in_reply_to_id}\n")
            f.write(f"media_ids: {media_ids}\n")
            f.write("----------------------\n")
            f.write(status)

        return RtStatus(id=str(current_call_id), url=f"https://foo.com/{current_call_id}")

    def media_post(self, media_file: str, description:str) -> RtMedia:
        self.media_calls.append(media_file)
        current_id = len(self.media_calls)
        output_path = self._output_path / f"image_{current_id}.txt"

        filename = media_file.split("/")[-1]
        with output_path.open("w", encoding="utf-8") as f:
            f.write(f"id: {current_id}\n")
            f.write(f"media_file: {filename}\n")
            f.write(f"description: {description}\n")
        return RtMedia(id=str(current_id), file_path=Path(media_file))

    def get_auth_url(self) -> str:
        self.auth_url_call_count += 1
        return "https://foo.bar/blah"

    def log_in(self, code: str, to_file: str) -> None:
        self.login_calls.append([code, to_file])
