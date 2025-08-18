from pathlib import Path
from typing import cast


class MastodonMixin:
    def split_username(self, full_username: str) -> tuple[str, str]:
        # if it starts with an @, remove that
        if full_username[0] == '@':
            full_username = full_username[1:]

        username, server = full_username.split('@')
        return username, server

    @property
    def bot_config_exists(self) -> bool:
        return self.bot_config_path.exists()

    @property
    def bot_config_path(self) -> Path:
        bot_path = cast(Path, getattr(self, 'bot_path'))
        return bot_path / 'mastodon.app'
