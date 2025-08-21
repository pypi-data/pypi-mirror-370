from .base import FdaSection


class UnknownSection(FdaSection):
    MULTIPLE = True

    def load(self) -> None:
        # Simply skip the body as we have no idea what it does
        self.fs.seek(0, 2)
