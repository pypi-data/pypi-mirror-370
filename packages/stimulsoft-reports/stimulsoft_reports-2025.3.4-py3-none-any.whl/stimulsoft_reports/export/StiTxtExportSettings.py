from ..enums.Encoding import Encoding
from .enums.StiExportFormat import StiExportFormat
from .enums.StiTxtBorderType import StiTxtBorderType
from .StiExportSettings import StiExportSettings


class StiTxtExportSettings(StiExportSettings):
    """Class describes settings for export to Text format."""
    
### Properties

    encoding = Encoding.UTF8
    """[enum] Gets or sets encoding of result text file."""

    drawBorder = True
    """Gets or sets value which indicates that borders will be drawn or not."""

    borderType = StiTxtBorderType.UNICODE_SINGLE
    """[enum] Gets or sets type of drawing border."""

    killSpaceLines = True
    """Gets or sets value which indicates that empty space lines will be removed."""

    killSpaceGraphLines = True
    """Gets or sets value which indicates that empty graph space lines will be removed."""        

    putFeedPageCode = True
    """Gets or sets value which indicates that special FeedPageCode marker will be placed in result file."""

    cutLongLines = True
    """Gets or sets value which indicates that long text lines will be cut."""

    zoomX = 1.0
    """Gets or sets horizontal zoom factor by X axis. By default a value is 1.0f what is equal 100% in export settings window."""

    zoomY = 1.0
    """Gets or sets vertical zoom factor by Y axis. By default a value is 1.0f what is equal 100% in export settings window."""

    useEscapeCodes = False
    """Gets or sets value which indicates that Escape codes will be used."""

    escapeCodesCollectionName = ''
    """Gets or sets value which indicates a EscapeCodesCollection name."""
    

### Helpers

    def getExportFormat(self):
        return StiExportFormat.TEXT