
from mastodon import Mastodon
from mastodon.return_types import Status

from robotooter.mastodon.mixin import MastodonMixin
from robotooter.models.configs import BotConfig
from robotooter.models.statuses import RtMedia, RtStatus


class MastodonManager(MastodonMixin):
    def __init__(self, bot_config: BotConfig) -> None:
        if not bot_config.username:
            raise RuntimeError("Username is not set")

        self.bot_config = bot_config
        self.bot_path = bot_config.working_directory
        self._client: Mastodon | None = None
        self.username, self.server = self.split_username(bot_config.username)

    @property
    def client(self) -> Mastodon:
        if self._client is None:
            self._client = Mastodon(access_token=str(self.bot_config_path))

        return self._client

    def toot(self, status: RtStatus | str) -> RtStatus:
        if isinstance(status, str):
            status = RtStatus(text=status)

        if len(status.media):
            for i, media in enumerate(status.media):
                if not media.id:
                    status.media[i] = self.post_media(media)
        media_ids = [m.id for m in status.media]

        m_status = self.client.status_post(
            status = status.text,
            in_reply_to_id=status.in_reply_to_id,
            media_ids=media_ids,
            spoiler_text=status.spoiler_text,
            quote_id=status.quote_id,
            visibility=status.visibility,
        )
        return self._adapt_status(status, m_status)

    def thread(self, toots: list[RtStatus]) -> None:
        in_reply_to_id = None
        for i, toot in enumerate(toots):
            toot.in_reply_to_id = in_reply_to_id
            status = self.toot(toot)
            toots[i] = status
            in_reply_to_id = status.id

    def post_media(self, media: RtMedia) -> RtMedia:
        m_media = self.client.media_post(
            media_file=str(media.file_path),
            description=media.description,
        )
        media.id = m_media.id
        return media

    def _adapt_status(self, rt_status: RtStatus, m_status: Status) -> RtStatus:
        rt_status.id = m_status.id
        rt_status.url = m_status.url
        return rt_status

