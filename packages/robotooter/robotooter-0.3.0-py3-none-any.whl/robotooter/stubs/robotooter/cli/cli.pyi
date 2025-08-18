from _typeshed import Incomplete

from robotooter import RoboTooter as RoboTooter
from robotooter.bots.base_bot import BaseBot as BaseBot
from robotooter.rt import load_robo_tooter as load_robo_tooter

parser: Incomplete
subparsers: Incomplete
plugins_parser: Incomplete
plugins_subparsers: Incomplete
register_parser: Incomplete
remove_parser: Incomplete
list_plugin_parser: Incomplete
list_parser: Incomplete

def require_bot(robo: RoboTooter, bot_name: str) -> BaseBot | None: ...
def find_bot_param(arguments: list[str]) -> tuple[str | None, list[str]]: ...
def find_working_dir(arguments: list[str]) -> tuple[str | None, list[str]]: ...
def find_param(arguments: list[str], flags: list[str]) -> tuple[str | None, list[str]]: ...
def main(arguments: list[str] | None = None) -> None: ...
def call_cli() -> None: ...
