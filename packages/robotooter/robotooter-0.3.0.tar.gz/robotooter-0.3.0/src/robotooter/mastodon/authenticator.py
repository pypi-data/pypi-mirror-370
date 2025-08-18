from pathlib import Path

from mastodon import Mastodon

from robotooter.mastodon.mixin import MastodonMixin


class Authenticator(MastodonMixin):
    def __init__(self, main_path: Path, bot_path: Path, full_username: str) -> None:
        self.main_path = main_path
        self.bot_path = bot_path
        self.full_username = full_username

        self._client: Mastodon | None = None

        self.username, self.server = self.split_username(full_username)

    def get_auth_url(self) -> str:
        return self.client.auth_request_url()

    def log_in(self, code: str) -> None:
        self.client.log_in(
            code=code,
            to_file=str(self.bot_config_path)
        )

    @property
    def client(self) -> Mastodon:
        if self._client is None:
            self._client = self.get_or_create_app()

        return self._client

    def get_or_create_app(self) -> Mastodon:
        app_config_path = self.server_config_path
        app_config_path.parent.mkdir(parents=True, exist_ok=True)

        if not app_config_path.exists():
            self.create_app()

        return Mastodon(str(app_config_path))

    def create_app(self) -> None:
        api_base_url = 'https://' + self.server
        Mastodon.create_app(
            'RoboTooter',
            to_file=str(self.server_config_path),
            api_base_url=api_base_url,
        )

    @property
    def server_config_path(self) -> Path:
        return self.main_path / "apps" / f"{self.server}.app"

