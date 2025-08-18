from argparse import Namespace
from typing import Any

import markovify
from _typeshed import Incomplete

from robotooter.bots.base_bot import BaseBot as BaseBot
from robotooter.bots.markov.markov_processor import MarkovProcessor as MarkovProcessor
from robotooter.filters.base_filter import BaseFilter as BaseFilter
from robotooter.models.configs import BotConfig as BotConfig
from robotooter.models.configs import ConfigT
from robotooter.util import download_sources as download_sources

class MarkovBot(BaseBot):
    @classmethod
    def create_with_config(cls, config_data: ConfigT, filters: list[BaseFilter]) -> 'BaseBot[Any]': ...

    NAME: str
    @staticmethod
    def new_bot_info() -> str | None: ...
    source_dir: Incomplete
    consolidated_file_path: Incomplete
    model_path: Incomplete
    def __init__(self, config: BotConfig, filters: list[BaseFilter]) -> None: ...
    def generate_toot(self) -> list[str]: ...
    @property
    def processor(self) -> MarkovProcessor: ...
    @property
    def model_exists(self) -> bool: ...
    @property
    def model(self) -> markovify.Text: ...
    def _setup_data(self, args: Namespace) -> None: ...
    def _toot(self, args: Namespace) -> None: ...
