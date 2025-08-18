import argparse

from robotooter.bots.base_bot import COUNT_PARAM, BaseBot, command
from robotooter.filters.base_filter import BaseFilter
from robotooter.models.configs import BotConfig


class FakeBotConfig(BotConfig):
    extra_field_1: str = ''


class FakeBot(BaseBot[FakeBotConfig]):
    NAME = "FakeBot"
    DESCRIPTION = "FakeBot bot"

    CONFIG_CLASS = FakeBotConfig

    @classmethod
    def create_with_config(cls, config_data: BotConfig, filters: list[BaseFilter]) -> 'FakeBot':
        config = FakeBotConfig(**config_data.model_dump())
        return cls(config, filters)

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-v1", "--value_one", type=float, default=1.0)
        parser.add_argument("-v2", "--value_two", type=str)

    def __init__(self, config: FakeBotConfig, filters: list[BaseFilter]):
        super().__init__(config, filters)
        self.number = 1

        self.command_overrides['toot'] = [
            ('-bk', '--book', {'type': str, 'help': 'Book'}),
            ('-cp', '--chapter', {'type': str, 'help': 'Chapter'}),
        ]

    def _setup_data(self, args: argparse.Namespace) -> None:
        assert args.value_one
        assert args.value_two

    def _toot(self, args: argparse.Namespace) -> None:
        assert args.chapter
        assert args.book

    @command(name='add_one', help_text='This is the custom help text.')
    def add_one(self, args: argparse.Namespace) -> None:
        self.number += 1

    @command(name='set_number', help_text='Set the number of the bot.', params=[COUNT_PARAM])
    def set_number(self, args: argparse.Namespace) -> None:
        self.number = args.count
