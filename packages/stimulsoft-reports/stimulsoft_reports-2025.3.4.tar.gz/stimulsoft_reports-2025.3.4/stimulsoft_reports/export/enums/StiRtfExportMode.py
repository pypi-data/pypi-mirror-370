from enum import Enum


class StiRtfExportMode(Enum):
    """Enumeration for setting modes of the RTF export."""
    
    TABLE = 4
    FRAME = 1
    WIN_WORD = 2
    TABBED_TEXT = 3