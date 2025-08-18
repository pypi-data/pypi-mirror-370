from pathlib import Path
from typing import TypeVar

from robotooter.models.saveable_model import SaveableModel


class BotConfig(SaveableModel):
    bot_name: str
    bot_class: str
    username: str | None = None
    maintainer: str | None = None
    working_directory: Path
    tags: list[str] | None = None
    toot_prepend: str | None = None
    toot_append: str | None = None
    filter_names: list[str] = []

    model_config = {
        "extra": "allow"
    }


ConfigT = TypeVar('ConfigT', bound=BotConfig)


class RoboTooterConfig(SaveableModel):
    working_directory: Path
    plugin_filters: list[str] = []
    plugin_bots: list[str] = []
