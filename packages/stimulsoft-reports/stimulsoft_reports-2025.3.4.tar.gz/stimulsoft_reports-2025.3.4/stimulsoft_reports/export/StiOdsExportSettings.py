from .enums.StiExportFormat import StiExportFormat
from .StiExportSettings import StiExportSettings


class StiOdsExportSettings(StiExportSettings):
    """Class describes settings for export to OpenDocument Calc format."""

### Properties

    imageQuality = 0.75
    """Gets or sets image quality of images which will be exported to ODS file."""

    imageResolution = 100
    """Gets or sets image resolution of images which will be exported to ODS file."""


### Helpers

    def getExportFormat(self):
        return StiExportFormat.ODS