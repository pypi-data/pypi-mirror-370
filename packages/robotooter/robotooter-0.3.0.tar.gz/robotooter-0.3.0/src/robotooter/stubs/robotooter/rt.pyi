from typing import Any

from _typeshed import Incomplete

from robotooter.bots.base_bot import BaseBot as BaseBot
from robotooter.filters.base_filter import BaseFilter as BaseFilter
from robotooter.models.configs import BotConfig as BotConfig
from robotooter.models.configs import RoboTooterConfig as RoboTooterConfig
from robotooter.util import load_included as load_included
from robotooter.util import load_list as load_list

class RoboTooter:
    __version__: str
    config: Incomplete
    filters: dict[str, type[BaseFilter]]
    bots: dict[str, type[BaseBot]]
    def __init__(self, config: RoboTooterConfig) -> None: ...
    @property
    def is_configured(self) -> bool: ...
    def save_configuration(self) -> None: ...
    def create_new_bot(self,
        bot_name: str,
        username: str,
        maintainer: str,
        bot_class: str,
        filter_names: list[str],
        tags: list[str] | None = None,
        toot_prepend: str | None = None,
        toot_append: str | None = None
    ) -> BaseBot: ...
    def load_bot(self, bot_name: str) -> BaseBot[Any]: ...
    def register_plugin(self, plugin_module: str) -> None: ...
    def unregister_plugin(self, plugin_module: str) -> None: ...
    def list_current_plugins(self) -> dict[str, list[str]]: ...
    def list_all_bots(self) -> list[BotConfig]: ...

def load_robo_tooter(root_dir: str | None = '~/.robotooter') -> RoboTooter: ...
