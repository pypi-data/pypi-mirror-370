import abc
import argparse
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, ClassVar, Generic, Protocol, TypeVar

from _typeshed import Incomplete

from robotooter.filters.base_filter import BaseFilter as BaseFilter
from robotooter.mastodon.manager import MastodonManager as MastodonManager
from robotooter.models.configs import BotConfig as BotConfig
from robotooter.models.configs import ConfigT as ConfigT

class CommandHandler(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
F = TypeVar('F', bound=Callable[..., Any])
CommandParam = tuple[str, str, dict[str, Any]]
CommandRegistry = dict[str, list[CommandParam]]

def command(name: str, help_text: str | None = None, params: list[CommandParam] | None = None) -> Callable[[F], F]: ...

COUNT_PARAM: CommandParam

class BaseBot(ABC, Generic[ConfigT], metaclass=abc.ABCMeta):
    NAME: str
    DESCRIPTION: str
    CONFIG_CLASS: ClassVar[type[BotConfig]]
    @classmethod
    @abstractmethod
    def create_with_config(cls, config_data: ConfigT, filters: list[BaseFilter]) -> BaseBot[Any]: ...
    @staticmethod
    def new_bot_info() -> str | None: ...
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None: ...
    config: Incomplete
    working_directory: Path
    data_root: Incomplete
    plugin_filters: Incomplete
    mastodon_manager: Incomplete
    command_handlers: dict[str, CommandHandler]
    command_overrides: CommandRegistry
    def __init__(self, config: ConfigT, filters: list[BaseFilter]) -> None: ...
    def setup_data(self, args: argparse.Namespace) -> None: ...
    def toot(self, args: argparse.Namespace) -> None: ...
    def install_package_resources(self) -> None: ...
    def parse_and_run(self, args_list: list[str]) -> None: ...
    def post_creation_hook(self) -> None: ...
