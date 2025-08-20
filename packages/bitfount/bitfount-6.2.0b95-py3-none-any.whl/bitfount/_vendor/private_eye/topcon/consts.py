from enum import Enum, unique


@unique
class ScanMode(str, Enum):
    """The mode of b-scan generation"""

    LINE: str = "Line"
    RECTANGULAR_VOLUME: str = "Rectangular volume"
    CYLINDRICAL_VOLUME: str = "Cylindrical volume"
    VERTICAL: str = "Vertical"
    SEVEN_LINE: str = "Seven line"
    DOUBLE_FIVE_LINE: str = "Double five line"
    CIRCLE: str = "Circle"
    NONE: str = "No B-Scan is present"
