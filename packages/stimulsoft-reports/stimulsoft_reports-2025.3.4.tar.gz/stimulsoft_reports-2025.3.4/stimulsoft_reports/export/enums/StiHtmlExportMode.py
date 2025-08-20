from enum import Enum


class StiHtmlExportMode(Enum):
    """Enumeration which sets an exported mode for the Html export."""

    SPAN = 1
    """A span tag of the HTML will be used for the exporting of the rendered document."""

    DIV = 2
    """A div tag of the HTML will be used for the exporting of the rendered document."""

    TABLE = 3
    """A table tag of the HTML will be used for the exporting of the rendered document."""

    FROM_REPORT = 4
    """A tag of the HTML will be taken from the report preview settings."""
