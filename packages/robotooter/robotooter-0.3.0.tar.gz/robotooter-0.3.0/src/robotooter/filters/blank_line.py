from robotooter.filters.base_filter import BaseFilter


class BlankLineFilter(BaseFilter):
    def process(self, line: str) -> str | None:
        if line.strip() == "":
            return None
        return line

    def finalize(self) -> str | None:
        return ''

    def reset(self) -> None:
        pass
