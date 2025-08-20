from enum import Flag


class StiDataExportMode(Flag):
    """Enumeration for setting modes of the data export."""

    DATA = 1
    HEADERS = 2
    DATA_AND_HEADERS = 3
    FOOTERS = 4
    HEADERS_FOOTERS = 6
    DATA_AND_HEADERS_FOOTERS = 7
    ALL_BANDS = 15
