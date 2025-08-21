from pathlib import Path
from typing import List

from ...private_eye.data import EntireFileOutputRequest, SeriesResult
from ...private_eye.output_formatter.output_formatter import EntireFileOutputWriter


class OutputNone(EntireFileOutputWriter):
    def output(self, result: SeriesResult, request: EntireFileOutputRequest) -> List[Path]:
        return []
