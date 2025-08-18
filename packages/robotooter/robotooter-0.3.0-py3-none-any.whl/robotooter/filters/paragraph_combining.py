from typing import List

from robotooter.filters.base_filter import BaseFilter

USE_NL = ['CHAPTER ', 'PART ']


class ParagraphCombiningFilter(BaseFilter):
    def __init__(self) -> None:
        self._buffer: List[str] = []

    def reset(self) -> None:
        self._buffer = []

    def process(self, line: str) -> str | None:
        stripped = line.strip()
        if stripped == "":
            if self._buffer:
                return self._join_buffer()
            return None
        else:
            self._buffer.append(stripped)
            return None  # Buffering, not yielding yet

    def finalize(self) -> str | None:
        if self._buffer:
            return self._join_buffer()
        return None

    def _join_buffer(self) -> str:
        first_line = self._buffer[0]
        joiner = ' '
        for nl in USE_NL:
            if first_line.startswith(nl):
                joiner = '\n'

        output = joiner.join(self._buffer) + '\n\n'
        self._buffer.clear()
        return output

