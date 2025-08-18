from abc import ABC

from robotooter.bots.base_bot import BaseBot


class BasePlugin(BaseBot, ABC):
    filters: list[str] = []
    bots: list[str] = []
