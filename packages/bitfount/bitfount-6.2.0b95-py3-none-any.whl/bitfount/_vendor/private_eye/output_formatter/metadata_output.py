import binascii
import json
import logging
from abc import ABC
from pathlib import Path
from typing import Any, Dict, List, Optional

import attr
from ...private_eye.data import EntireFileOutputRequest, SeriesResult
from ...private_eye.output_formatter.output_formatter import EntireFileOutputWriter
from ...private_eye.utils.attrs import is_json_ignored

logger = logging.getLogger(__name__)


class OutputMetadata(EntireFileOutputWriter, ABC):
    def _as_json(self, result: SeriesResult) -> str:
        result_as_dict: Dict[str, Any] = {**attr.asdict(result, filter=_not_json_ignored, recurse=True)}
        return json.dumps(result_as_dict, indent=4, default=_format_by_type)


class OutputMetadataConsole(OutputMetadata):
    def output(self, result: SeriesResult, request: EntireFileOutputRequest) -> List[Path]:
        print(self._as_json(result))
        return []


class OutputMetadataJSON(OutputMetadata):
    def output(self, result: SeriesResult, request: EntireFileOutputRequest) -> List[Path]:
        output_path_prefix = request.output_path_prefix
        output_file_path = output_path_prefix.with_name(output_path_prefix.name + ".json")
        with output_file_path.open("w") as output_file:
            output_file.write(self._as_json(result))

        return [output_file_path]


def _not_json_ignored(at: attr.Attribute, v: Any) -> bool:
    return not is_json_ignored(at)


def _format_by_type(obj: Any) -> Optional[str]:
    if isinstance(obj, bytes):
        bin_string = binascii.hexlify(obj).decode("ascii").upper()
        return " ".join([bin_string[i : i + 2] for i in range(0, len(bin_string), 2)])
    return str(obj)
