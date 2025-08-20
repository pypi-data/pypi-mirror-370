from .enums.StiExportFormat import StiExportFormat
from .enums.StiRtfExportMode import StiRtfExportMode
from .StiExportSettings import StiExportSettings


class StiRtfExportSettings(StiExportSettings):
    """Class describes settings for export to RTF format."""
    
### Properties

    codePage = 0
    """Gets or sets code page of RTF file."""

    exportMode = StiRtfExportMode.TABLE
    """[enum] Gets or sets mode of RTF file creation."""

    usePageHeadersAndFooters = False
    """
    Gets or sets value which enables special mode of exporting page headers and page footers into result file.
    In this mode export engine try to insert all page headers and footers as RTF headers and footers.
    """

    imageQuality = 0.75
    """Gets or sets image quality of images which will be exported to result file."""

    imageResolution = 100
    """Gets or sets image resolution of images which will be exported to result file."""

    removeEmptySpaceAtBottom = True
    """Gets or sets a value indicating whether it is necessary to remove empty space at the bottom of the page."""

    storeImagesAsPng = False
    """Gets or sets a value indicating whether it is necessary to store images in PNG format."""
    

### Helpers

    def getExportFormat(self):
        return StiExportFormat.RTF