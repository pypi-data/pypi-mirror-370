from .enums.StiExportFormat import StiExportFormat
from .enums.StiWordRestrictEditing import StiWordRestrictEditing
from .StiExportSettings import StiExportSettings


class StiWordExportSettings(StiExportSettings):
    """Class describes settings for export to Microsoft Word formats."""

### Properties

    usePageHeadersAndFooters = False
    """Gets or sets value which indicates that one (first) page header and page footer from report will be used in word file."""

    imageQuality = 0.75
    """Gets or sets image quality of images which will be exported to result file."""

    imageResolution = 100
    """Gets or sets image resolution of images which will be exported to result file."""
    
    imageFormat = None
    """Gets or sets image format for exported images. 'None' corresponds to automatic mode."""

    removeEmptySpaceAtBottom = True
    """Gets or sets a value indicating whether it is necessary to remove empty space at the bottom of the page."""

    companyString = 'Stimulsoft'
    """Gets or sets information about the creator to be inserted into result Word file."""
    
    lastModifiedString: str = None
    
    restrictEditing = StiWordRestrictEditing.NO
    """[enum]"""

    protectionPassword = '*TestPassword*'

    encryptionPassword: str = None


### Helpers

    def getExportFormat(self):
        return StiExportFormat.WORD