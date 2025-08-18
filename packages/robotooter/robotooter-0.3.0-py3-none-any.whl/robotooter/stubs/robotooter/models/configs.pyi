from pathlib import Path
from typing import TypeVar

from robotooter.models.saveable_model import SaveableModel as SaveableModel

class BotConfig(SaveableModel):
    bot_name: str
    bot_class: str
    username: str | None
    maintainer: str | None
    working_directory: Path
    tags: list[str] | None
    toot_prepend: str | None
    toot_append: str | None
    filter_names: list[str]
    class Config:
        extra: str
ConfigT = TypeVar('ConfigT', bound=BotConfig)

class RoboTooterConfig(SaveableModel):
    working_directory: Path
    plugin_filters: list[str]
    plugin_bots: list[str]
