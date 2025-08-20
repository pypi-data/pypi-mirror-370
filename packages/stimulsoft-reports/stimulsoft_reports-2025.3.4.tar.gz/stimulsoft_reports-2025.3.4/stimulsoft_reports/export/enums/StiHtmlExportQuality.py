from enum import Enum


class StiHtmlExportQuality(Enum):
    """Enumeration which sets a quality of images which will be exported."""

    HIGH = 1
    """Sets a high quality of the exported images."""

    LOW = 2
    """Sets a low quality of the exported images."""