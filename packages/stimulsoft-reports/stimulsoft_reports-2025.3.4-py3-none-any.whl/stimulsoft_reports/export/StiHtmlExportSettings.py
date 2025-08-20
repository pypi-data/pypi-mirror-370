from ..enums.Encoding import Encoding
from .enums.StiExportFormat import StiExportFormat
from .enums.StiHorAlignment import StiHorAlignment
from .enums.StiHtmlChartType import StiHtmlChartType
from .enums.StiHtmlExportBookmarksMode import StiHtmlExportBookmarksMode
from .enums.StiHtmlExportMode import StiHtmlExportMode
from .enums.StiHtmlExportQuality import StiHtmlExportQuality
from .enums.StiHtmlType import StiHtmlType
from .enums.StiImageFormat import ImageFormat
from .StiExportSettings import StiExportSettings


class StiHtmlExportSettings(StiExportSettings):
    """Class describes settings for export to HTML formats."""

### Properties

    htmlType: StiHtmlType = None
    """[enum] Gets or sets type of the exported html file."""

    imageQuality = 0.75
    """Gets or sets image quality of images which will be exported to result file."""

    imageResolution = 100
    """Gets or sets image resolution of images which will be exported to result file."""

    imageFormat = ImageFormat.PNG
    """[enum] Gets or sets image format for exported images."""

    encoding = Encoding.UTF8
    """[enum] Gets or sets encoding of html file."""

    zoom = 1.0
    """Gets or sets zoom factor of exported file. HTML5 export mode is not supported."""

    exportMode = StiHtmlExportMode.DIV
    """[enum] Gets or sets mode of html file creation. HTML5 export mode is not supported."""

    exportQuality = StiHtmlExportQuality.HIGH
    """[enum] Gets or sets quality of html file. HTML5 export mode is not supported."""

    addPageBreaks = True
    """Gets or sets value which indicates that special page breaks marker will be added to result html file. HTML5 export mode is not supported."""

    bookmarksTreeWidth = 150
    """Gets or sets default width of bookmarks tree. HTML5 export mode is not supported."""

    exportBookmarksMode = StiHtmlExportBookmarksMode.ALL
    """[enum] Gets or sets export mode of bookmarks tree. HTML5 export mode is not supported."""

    useStylesTable = True
    """Gets or sets value which indicates that table styles will be used in result html file. HTML5 and MHT export mode is not supported."""

    removeEmptySpaceAtBottom = True
    """Gets or sets a value indicating whether it is necessary to remove empty space at the bottom of the page. HTML5 and MHT export mode is not supported."""

    pageHorAlignment = StiHorAlignment.LEFT
    """[enum] Gets or sets the horizontal alignment of pages. HTML5 and MHT export mode is not supported."""

    compressToArchive = False
    """Gets or sets a value indicating whether it is necessary to save output file as zip-file. HTML5 and MHT export mode is not supported."""

    useEmbeddedImages = True
    """Gets or sets a value indicating whether it is necessary to save images as embedded data in html file. HTML5 and MHT export mode is not supported."""

    continuousPages = True
    """Gets or sets value which indicates that all report pages will be shown as vertical ribbon. HTML and MHT export mode is not supported."""

    chartType = StiHtmlChartType.ANIMATED_VECTOR
    """[enum]"""

    openLinksTarget = ''
    """Gets or sets a target to open links from the exported report."""

    useWatermarkMargins = False


### Helpers

    def getExportFormat(self):
        if self.htmlType == StiHtmlType.HTML5:
            return StiExportFormat.HTML5
        
        return StiExportFormat.HTML
    
    def setHtmlType(self, format = None):
        if format == None:
            format = self.getExportFormat()
        
        if format == StiExportFormat.HTML5:
            self.htmlType = StiHtmlType.HTML5
            
        elif format == StiExportFormat.HTML:
            self.htmlType = StiHtmlType.HTML


### HTML

    def getHtml(self) -> str:
        self.setHtmlType()

        return super().getHtml()
    

### Constructor

    def __init__(self, htmlType: StiHtmlType = None):
        """
        htmlType:
            [enum] Type of the exported HTML file.
        """

        super().__init__()
        self.htmlType = htmlType