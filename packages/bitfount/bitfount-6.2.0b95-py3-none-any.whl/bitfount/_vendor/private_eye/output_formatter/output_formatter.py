from abc import ABC, abstractmethod
import numpy as np
from pathlib import Path
from typing import Dict, List, Union

from ...private_eye.data import EntireFileOutputRequest, ImageProcessingOptions, IndividualImageOutputRequest, SeriesResult


class EntireFileOutputWriter(ABC):
    @abstractmethod
    def output(self, result: SeriesResult, request: EntireFileOutputRequest) -> List[Path]:
        raise NotImplementedError()


class IndividualImageOutputWriter(ABC):
    @abstractmethod
    def output(
        self, result: SeriesResult, request: IndividualImageOutputRequest, save_to_file: bool = True
    ) -> List[Union[Dict[ImageProcessingOptions, Path], Dict[str, np.ndarray]]]:
        raise NotImplementedError()
