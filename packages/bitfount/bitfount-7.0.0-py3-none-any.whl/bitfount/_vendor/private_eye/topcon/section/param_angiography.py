from ....private_eye.topcon.section.base import FdaSection


class ParamAngiographySection(FdaSection):
    def load(self) -> None:
        # TODO RIPF-1590 Learn to parse this section
        self.fs.seek(0, 2)
