from enum import Enum


class StiImageResolutionMode(Enum):
    """Enumeration for setting modes of using of image resolution."""
    
    EXACTLY = 1
    NO_MORE_THAN = 2
    AUTO = 3