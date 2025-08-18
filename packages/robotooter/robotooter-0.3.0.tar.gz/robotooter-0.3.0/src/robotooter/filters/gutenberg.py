from robotooter.filters.base_filter import BaseFilter

PG_START = "*** START OF THE PROJECT GUTENBERG EBOOK"
PG_END = "*** END OF THE PROJECT GUTENBERG EBOOK"


class GutenbergFilter(BaseFilter):
    """
    For this we read in each file until we find the end of the Project Gutenberg header.
    Then we keep reading, and write to our combined file. We stop when we're back to boilerplace.
    """
    def __init__(self) -> None:
        self._write_file = False
        self._in_note = False

    def process(self, line: str) -> str | None:
        if self._should_send(line):
            return line

        return None

    def reset(self) -> None:
        self._write_file = False
        self._in_note = False

    def _should_send(self, line: str) -> bool:
        line = line.strip()

        if not line:
            return self._write_file

        if line.find(PG_END) > -1:
            self._write_file = False
            return False

        if line.find('*') > -1:
            pass

        if self._write_file:
            if line[0] == '*':
                return False

            if line.find('[') > -1:
                self._in_note = True

            if line.find(']') > -1:
                self._in_note = False
                return False

        if self._write_file and not self._in_note:
            return True

        if line.find(PG_START) > -1:
            self._write_file = True

        return False
