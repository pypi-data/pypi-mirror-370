from .enums.StiExportFormat import StiExportFormat
from .StiExportSettings import StiExportSettings


class StiOdtExportSettings(StiExportSettings):
    """Class describes settings for export to OpenDocument Writer format."""

### Properties

    usePageHeadersAndFooters = False
    """Gets or sets value which indicates that one (first) page header and page footer from report will be used in ODT file."""

    imageQuality = 0.75
    """Gets or sets image quality of images which will be exported to ODT file."""

    imageResolution = 100
    """Gets or sets image resolution of images which will be exported to ODT file."""

    removeEmptySpaceAtBottom = True
    """Gets or sets a value indicating whether it is necessary to remove empty space at the bottom of the page."""


### Helpers

    def getExportFormat(self):
        return StiExportFormat.ODT