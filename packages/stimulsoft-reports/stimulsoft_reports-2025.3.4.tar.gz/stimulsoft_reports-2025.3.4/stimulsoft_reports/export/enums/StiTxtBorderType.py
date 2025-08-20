from enum import Enum


class StiTxtBorderType(Enum):
    """Enumeration describes a type of the border."""

    SIMPLE = 1
    """A border which consists of "+","-","|" symbols."""

    UNICODE_SINGLE = 2
    """A border which consists of character graphics symbols. A Single type of the border."""

    UNICODE_DOUBLE = 3
    """A border consists of character graphics symbols. A Double type of the border."""