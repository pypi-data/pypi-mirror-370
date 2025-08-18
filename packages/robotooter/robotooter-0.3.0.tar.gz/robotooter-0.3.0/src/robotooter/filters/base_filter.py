from abc import ABC, abstractmethod


class BaseFilter(ABC):
    def process(self, line: str) -> str | None:
        """Override this"""
        return line

    def finalize(self) -> str | None:
        return ''

    @abstractmethod
    def reset(self) -> None:
        pass

