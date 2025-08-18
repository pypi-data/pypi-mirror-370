import argparse
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, ClassVar, Generic, Protocol, Type, TypeVar

from robotooter.filters.base_filter import BaseFilter
from robotooter.mastodon.manager import MastodonManager
from robotooter.models.configs import BotConfig, ConfigT


class CommandHandler(Protocol):
    _command_name: str
    _command_help: str
    _command_params: list[tuple[str, str, dict[str, Any]]] | None

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


F = TypeVar('F', bound=Callable[..., Any])
CommandParam = tuple[str, str, dict[str, Any]]
CommandRegistry = dict[str, list[CommandParam]]


def command(
        name: str,
        help_text: str | None = None,
        params: list[CommandParam] | None = None
) -> Callable[[F], F]:
    """Decorator to register a method as a command handler with help text."""
    def decorator(func: F) -> F:
        setattr(func, '_command_name', name)
        setattr(func, '_command_help', help_text or func.__doc__ or f"Execute {name} command")
        setattr(func, '_command_params', params or [])
        return func
    return decorator


COUNT_PARAM: CommandParam = ('-c', '--count', {'default': 1, 'type': int, 'help': 'Quantity'})


class BaseBot(ABC, Generic[ConfigT]):
    NAME = "BaseTooter"
    DESCRIPTION = "BaseTooter bot"

    CONFIG_CLASS: ClassVar[Type[BotConfig]] = BotConfig

    @classmethod
    @abstractmethod
    def create_with_config(cls, config_data: ConfigT, filters: list[BaseFilter]) -> 'BaseBot[Any]':
        pass

    @staticmethod
    def new_bot_info() -> str | None:
        return None

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """Override this to add bot-specific arguments."""
        pass

    def __init__(self, config: ConfigT, filters: list[BaseFilter]) -> None:
        self.config = config
        self.config.filename = config.filename
        self.working_directory: Path = config.working_directory
        self.data_root = Path(os.path.join(self.working_directory, "data"))
        self.plugin_filters = filters
        self.mastodon_manager = MastodonManager(self.config)

        self.command_handlers: dict[str, CommandHandler] = {}
        self.command_overrides: CommandRegistry = {}

    @command('setup', 'Initialize bot configuration')
    def setup_data(self, args: argparse.Namespace) -> None:
        self._setup_data(args)

    @command('toot', 'Send a toot', params=[COUNT_PARAM])
    def toot(self, args: argparse.Namespace) -> None:
        self._toot(args)

    @abstractmethod
    def _setup_data(self, args: argparse.Namespace) -> None:
        pass

    @abstractmethod
    def _toot(self, args: argparse.Namespace) -> None:
        pass

    def install_package_resources(self) -> None:
        pass

    def parse_and_run(self, args_list: list[str]) -> None:
        self._register_commands()
        parser = argparse.ArgumentParser(prog=f'robotooter -b {self.config.bot_name}')

        # Add bot-specific arguments
        self.add_arguments(parser)

        # Add subparsers for commands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        for cmd_name, handler in self.command_handlers.items():
            help_text = getattr(handler, '_command_help', f'Execute {cmd_name}')
            sub_parser = subparsers.add_parser(cmd_name, help=help_text)
            if cmd_name in self.command_overrides:
                params = self.command_overrides[cmd_name]
            else:
                params = getattr(handler, '_command_params')
            if params:
                for short, long, attrs in params:
                    sub_parser.add_argument(short, long, **attrs)


        args, remaimder = parser.parse_known_args(args_list)

        if args.command in self.command_handlers:
            self.command_handlers[args.command](args)
            return

        parser.print_help()

    def post_creation_hook(self) -> None:
        pass

    def _register_commands(self) -> None:
        if not self.command_handlers:
            for attr_name in dir(self):
                attr = getattr(self, attr_name)
                if hasattr(attr, '_command_name'):
                    self.command_handlers[attr._command_name] = attr

