from enum import Enum


class StiDataType(Enum):
    """Enumeration describes a type of the data exports."""

    CSV = 1
    DBF = 2
    DIF = 3
    SYLK = 4
    XML = 5
    JSON = 6