import os
from pathlib import Path
from typing import Any

from robotooter.bots.base_bot import BaseBot
from robotooter.filters.base_filter import BaseFilter
from robotooter.models.configs import BotConfig, RoboTooterConfig
from robotooter.util import load_included, load_list


class RoboTooter:
    __version__ = "0.2.0"
    def __init__(self, config: RoboTooterConfig) -> None:
        if config is None:
            config = RoboTooterConfig(
                working_directory=Path(os.path.expanduser("~/.robotooter")),
            )
        self.config = config
        self.filters: dict[str, type[BaseFilter]] = {}
        self.bots: dict[str, type[BaseBot]] = {}

        self._import_filters()
        self._import_bots()

    @property
    def is_configured(self) -> bool:
        return os.path.exists(self.config.working_directory / "config.json")

    def save_configuration(self) -> None:
        if not os.path.exists(self.config.working_directory):
            os.makedirs(self.config.working_directory)

        if not self.config.filename:
            self.config.filename = self.config.working_directory / "config.json"
        self.config.save()

    def create_new_bot(
        self,
        bot_name: str,
        username: str,
        maintainer: str,
        bot_class: str,
        filter_names: list[str],
        tags: list[str] | None = None,
        toot_prepend: str | None = None,
        toot_append: str | None = None,
    ) -> BaseBot:
        if bot_class not in self.bots.keys():
            raise ValueError(f"Invalid bot class {bot_class}")
        for filter_name in filter_names:
            if filter_name not in self.filters.keys():
                raise ValueError(f"Invalid filter name {filter_name}")

        bot_working_directory = self.config.working_directory / bot_name
        os.makedirs(bot_working_directory, exist_ok=True)

        if tags is None:
            tags = []

        if username[0] != '@':
            username = f"@{username}"
        if maintainer[0] != '@':
            maintainer = f"@{maintainer}"

        bot_config = BotConfig(
            bot_name=bot_name,
            bot_class=bot_class,
            filter_names=filter_names,
            username=username,
            working_directory=bot_working_directory,
            tags=tags,
            toot_prepend=toot_prepend,
            toot_append=toot_append,
            maintainer=maintainer,
        )
        self._save_bot_config(bot_config)
        new_bot = self.load_bot(bot_name)
        new_bot.install_package_resources()
        new_bot.post_creation_hook()
        return self.load_bot(bot_name)

    def load_bot(self, bot_name: str) -> BaseBot[Any]:
        bot_config = self._load_bot_config(bot_name)
        bot_class = self.bots[bot_config.bot_class]
        bot_filters: list[BaseFilter] = []
        for filter_name in bot_config.filter_names:
            bot_filters.append(self.filters[filter_name]())

        return bot_class.create_with_config(bot_config, bot_filters)

    def register_plugin(self, plugin_module: str) -> None:
        plugin_info = self._get_plugin_classes(plugin_module)
        if not plugin_info:
            raise RuntimeError(f"{plugin_module} is not a valid plugin module")
        if 'filters' in plugin_info:
            self.config.plugin_filters.extend(plugin_info['filters'])
        if 'bots' in plugin_info:
            self.config.plugin_bots.extend(plugin_info['bots'])

        self.save_configuration()

    def unregister_plugin(self, plugin_module: str) -> None:
        plugin_info = self._get_plugin_classes(plugin_module)
        if 'filters' in plugin_info:
            for filter_name in plugin_info['filters']:
                if filter_name in self.config.plugin_filters:
                    self.config.plugin_filters.remove(filter_name)
        if 'bots' in plugin_info:
            for bot in plugin_info['bots']:
                if bot in self.config.plugin_bots:
                    self.config.plugin_bots.remove(bot)
        self.save_configuration()

    def list_current_plugins(self) -> dict[str, list[str]]:
        return {
            'filters': self.config.plugin_filters,
            'bots': self.config.plugin_bots,
        }

    def list_all_bots(self) -> list[BotConfig]:
        configs = []
        for file in self.config.working_directory.iterdir():
            if file.is_dir():
                config_path = file / "config.json"
                if config_path.exists():
                    configs.append(BotConfig.load(config_path))
        return configs

    def _import_filters(self) -> None:
        self.filters = load_included('robotooter.filters', BaseFilter, 'Filter')
        self.filters = self.filters | load_list(self.config.plugin_filters, BaseFilter)

    def _import_bots(self) -> None:
        self.bots = load_included('robotooter.bots', BaseBot, 'Bot')
        self.bots = self.bots | load_list(self.config.plugin_bots, BaseBot)

    def _save_bot_config(self, bot_config: BotConfig) -> None:
        if not bot_config.filename:
            bot_config.filename = self.config.working_directory / f"{bot_config.bot_name}/config.json"
        bot_config.save()

    def _load_bot_config(self, bot_name: str) -> BotConfig:
        return BotConfig.load(self.config.working_directory / f"{bot_name}/config.json")

    def _get_plugin_classes(self, plugin_module: str) -> dict[str, str]:
        import importlib
        plugin_klass = importlib.import_module(plugin_module)
        info = {}
        if hasattr(plugin_klass, "plugin_filters"):
            info['filters'] = plugin_klass.plugin_filters
        if hasattr(plugin_klass, "plugin_bots"):
            info['bots'] = plugin_klass.plugin_bots
        return info

def load_robo_tooter(root_dir: str | None = '~/.robotooter') -> RoboTooter:
    if not root_dir:
        root_dir = '~/.robotooter'
    config_path = Path(os.path.expanduser(root_dir)) / "config.json"
    config = RoboTooterConfig.load(config_path)
    return RoboTooter(config)
