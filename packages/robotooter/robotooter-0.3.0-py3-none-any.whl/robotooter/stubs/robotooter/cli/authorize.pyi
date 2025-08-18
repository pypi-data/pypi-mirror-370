from robotooter import RoboTooter as RoboTooter
from robotooter.bots.base_bot import BaseBot as BaseBot
from robotooter.cli.util import get_yes as get_yes
from robotooter.mastodon.authenticator import Authenticator as Authenticator

def run_authorize(rt: RoboTooter, bot: BaseBot, force: bool = False) -> None: ...
