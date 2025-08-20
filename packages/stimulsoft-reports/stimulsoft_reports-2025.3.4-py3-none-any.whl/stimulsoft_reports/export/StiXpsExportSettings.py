from .enums.StiExportFormat import StiExportFormat
from .StiExportSettings import StiExportSettings


class StiXpsExportSettings(StiExportSettings):
    """Class describes settings for export to XPS format."""

### Properties

    imageQuality = 0.75
    """Gets or sets image quality of images which will be exported to result file."""

    imageResolution = 100
    """Gets or sets image resolution of images which will be exported to result file."""

    exportRtfTextAsImage = False
    """Gets or sets value which indicates that RTF text will be exported as bitmap images or as vector images."""


### Helpers

    def getExportFormat(self):
        return StiExportFormat.XPS