from _typeshed import Incomplete
from mastodon import Mastodon
from mastodon.return_types import Status as Status

from robotooter.mastodon.mixin import MastodonMixin as MastodonMixin
from robotooter.models.configs import BotConfig as BotConfig
from robotooter.models.statuses import RtMedia as RtMedia
from robotooter.models.statuses import RtStatus as RtStatus

class MastodonManager(MastodonMixin):
    bot_config: Incomplete
    bot_path: Incomplete
    def __init__(self, bot_config: BotConfig) -> None: ...
    @property
    def client(self) -> Mastodon: ...
    def toot(self, status: RtStatus | str) -> RtStatus: ...
    def thread(self, toots: list[RtStatus]) -> None: ...
    def post_media(self, media: RtMedia) -> RtMedia: ...
