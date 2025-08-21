from ....consts import Laterality
from ....exceptions import ImageParseException


def parse_laterality(lat_str: str) -> Laterality:
    if lat_str == "L":
        return Laterality.LEFT
    if lat_str == "R":
        return Laterality.RIGHT
    raise ImageParseException(f"Unable to parse laterality: {lat_str}")
