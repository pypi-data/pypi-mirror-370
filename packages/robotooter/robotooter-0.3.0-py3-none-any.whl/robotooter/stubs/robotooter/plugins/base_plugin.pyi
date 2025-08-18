import abc
from abc import ABC

from robotooter.bots.base_bot import BaseBot as BaseBot

class BasePlugin(BaseBot, ABC, metaclass=abc.ABCMeta):
    filters: list[str]
    bots: list[str]
