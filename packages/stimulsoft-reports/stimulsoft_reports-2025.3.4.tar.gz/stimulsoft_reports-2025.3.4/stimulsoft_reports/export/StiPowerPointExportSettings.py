from .enums.StiExportFormat import StiExportFormat
from .enums.StiImageFormat import ImageFormat
from .StiExportSettings import StiExportSettings


class StiPowerPointExportSettings(StiExportSettings):
    """Class describes settings for export to Adobe PowerPoint format."""

### Properties

    imageQuality = 0.75
    """Gets or sets image quality of images which will be exported to result file."""

    imageResolution = 100
    """Gets or sets image resolution of images which will be exported to result file."""

    encryptionPassword: str = None

    imageFormat: ImageFormat = None
    """[enum] Gets or sets image format for exported images. 'None' corresponds to automatic mode."""


### Helpers

    def getExportFormat(self):
        return StiExportFormat.POWERPOINT