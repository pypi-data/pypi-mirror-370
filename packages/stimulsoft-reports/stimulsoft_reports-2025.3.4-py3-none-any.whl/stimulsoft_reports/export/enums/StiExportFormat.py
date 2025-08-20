from __future__ import annotations

import typing
from enum import Enum

from ...enums import StiReportType
from .StiDataType import StiDataType
from .StiHtmlType import StiHtmlType
from .StiImageType import StiImageType

if typing.TYPE_CHECKING:
    from ...export.StiExportSettings import StiExportSettings


class StiExportFormat(Enum):

### Constants

    NONE = 0
    """Export will not be done."""

    PDF = 1
    """Adobe PDF format."""

    XPS = 2
    """XPS (XML Paper Specification) format."""

    RTF = 6
    """RTF (Rich Text) format."""

    TEXT = 11
    """Text format."""

    EXCEL = 14
    """Microsoft Excel format."""

    WORD = 15
    """Microsoft Word format."""

    XML = 16
    """XML (Extensible Markup Language) format."""

    CSV = 17
    """CSV (Comma Separated Value) format."""

    DIF = 18
    """DIF format."""

    SYLK = 19
    """SYLK (Symbolic Link) format."""

    IMAGE = 20
    """Image format. The SVG format is used by default."""

    IMAGE_GIF = 21
    """Image in GIF (Graphics Interchange) format."""

    IMAGE_BMP = 22
    """Image in BMP (Windows Bitmap) format."""

    IMAGE_PNG = 23
    """Image in PNG (Portable Network Graphics) format."""

    IMAGE_TIFF = 24
    """Image in TIFF (Tagged Image File Format) format."""

    IMAGE_JPEG = 25
    """Image in JPEG (Joint Photographic Experts Group) format."""

    IMAGE_PCX = 26
    """Image in PCX (Picture Exchange) format."""

    IMAGE_SVG = 28
    """Image in SVG (Scalable Vector Graphics) format."""

    IMAGE_SVGZ = 29
    """Image in SVGZ (Compressed SVG) format."""

    DBF = 31
    """DBF (dBase/FoxPro) format."""

    HTML = 32
    """HTML format."""

    ODS = 33
    """OpenDocument Calc format."""

    ODT = 34
    """OpenDocument Writer format."""

    POWERPOINT = 35
    """Microsoft PowerPoint format."""

    HTML5 = 36
    """HTML5 format."""

    DATA = 37
    """Data format. The CSV format is used by default."""

    JSON = 38
    """JSON (JavaScript Object Notation) format."""

    DOCUMENT = 1000
    """Document MDC file."""
    

### Helpers

    def __getCorrectExportFormat(format: int) -> int:
        if format == 20 or format == StiExportFormat.IMAGE: return StiExportFormat.IMAGE_SVG
        if format == 37 or format == StiExportFormat.DATA: return StiExportFormat.CSV
        return format

    def __getFormatName(format: int) -> str:
        format = StiExportFormat.__getCorrectExportFormat(format)
        names = {value: name for name, value in vars(StiExportFormat).items() if name.isupper()}
        return names[format]

    def getFileExtension(format: int, settings: StiExportSettings = None) -> str:
        """Returns the file extension for the selected export format."""

        format = StiExportFormat.__getCorrectExportFormat(format)

        if format == StiExportFormat.TEXT: return 'txt'
        if format == StiExportFormat.EXCEL: return 'xlsx'
        if format == StiExportFormat.WORD: return 'docx'
        if format == StiExportFormat.HTML5: return 'html'
        if format == StiExportFormat.POWERPOINT: return 'pptx'
        if format == StiExportFormat.IMAGE_JPEG: return 'jpg'
        if format == StiExportFormat.DOCUMENT: return 'mdc'

        from ...export import StiImageExportSettings
        compressToArchive = isinstance(settings, StiImageExportSettings) and settings.compressToArchive

        return 'zip' if compressToArchive else StiExportFormat.__getFormatName(format).replace('IMAGE_', '').lower()

    def getMimeType(format: int, settings: StiExportSettings = None) -> str:
        """Returns the mime type for the selected export format."""

        format = StiExportFormat.__getCorrectExportFormat(format)

        from ...export import StiImageExportSettings
        compressToArchive = isinstance(settings, StiImageExportSettings) and settings.compressToArchive

        if format == StiExportFormat.PDF: return 'application/pdf'
        if format == StiExportFormat.XPS: return 'application/vnd.ms-xpsdocument'
        if format == StiExportFormat.RTF: return 'application/rtf'
        if format == StiExportFormat.TEXT: return 'text/plain'
        if format == StiExportFormat.EXCEL: return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        if format == StiExportFormat.WORD: return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        if format == StiExportFormat.XML: return 'application/xml'
        if format == StiExportFormat.CSV: return 'text/csv'
        if format == StiExportFormat.DIF: return 'text/x-diff'
        if format == StiExportFormat.SYLK: return 'application/x-sylk'
        if format == StiExportFormat.IMAGE_GIF: return 'application/x-zip' if compressToArchive else 'image/gif'
        if format == StiExportFormat.IMAGE_BMP: return 'application/x-zip' if compressToArchive else 'image/x-ms-bmp'
        if format == StiExportFormat.IMAGE_PNG: return 'application/x-zip' if compressToArchive else 'image/x-png'
        if format == StiExportFormat.IMAGE_TIFF: return 'application/x-zip' if compressToArchive else 'image/tiff'
        if format == StiExportFormat.IMAGE_JPEG: return 'application/x-zip' if compressToArchive else 'image/jpeg'
        if format == StiExportFormat.IMAGE_PCX: return 'application/x-zip' if compressToArchive else 'image/x-pcx'
        if format == StiExportFormat.IMAGE_SVG or format == StiExportFormat.IMAGE_SVGZ: return 'application/x-zip' if compressToArchive else 'image/svg+xml'
        if format == StiExportFormat.DBF: return 'application/dbf'
        if format == StiExportFormat.HTML or format == StiExportFormat.HTML5: return 'text/html'
        if format == StiExportFormat.ODS: return 'application/vnd.oasis.opendocument.spreadsheet'
        if format == StiExportFormat.ODT: return 'application/vnd.oasis.opendocument.text'
        if format == StiExportFormat.POWERPOINT: return 'application/vnd.ms-powerpoint'
        if format == StiExportFormat.JSON: return 'application/json'
        if format == StiExportFormat.DOCUMENT: return 'text/xml'

        return 'text/plain'

    def getFormatName(format: int) -> str:
        """Returns the name of the export format suitable for use in JavaScript code."""

        formatName: str = StiExportFormat.__getFormatName(format)
        result = formatName.lower().capitalize().replace('point', 'Point').split('_')
        return result[0] if len(result) == 1 else result[0] + result[1].capitalize()
    
    def getExportSettings(format, reportType = StiReportType.AUTO):
        """Returns the settings class for the specified export format."""

        format = StiExportFormat.__getCorrectExportFormat(format)

        if format == StiExportFormat.PDF:
            if reportType == StiReportType.DASHBOARD:
                from stimulsoft_dashboards.export import \
                    StiPdfDashboardExportSettings
                return StiPdfDashboardExportSettings()

            from ..StiPdfExportSettings import StiPdfExportSettings
            return StiPdfExportSettings()
        
        if format == StiExportFormat.XPS:
            from ..StiXpsExportSettings import StiXpsExportSettings
            return StiXpsExportSettings()
        
        if format == StiExportFormat.RTF:
            from ..StiRtfExportSettings import StiRtfExportSettings
            return StiRtfExportSettings()
        
        if format == StiExportFormat.TEXT:
            from ..StiTxtExportSettings import StiTxtExportSettings
            return StiTxtExportSettings()
        
        if format == StiExportFormat.EXCEL:
            if reportType == StiReportType.DASHBOARD:
                from stimulsoft_dashboards.export import StiExcelDashboardExportSettings
                return StiExcelDashboardExportSettings()
            
            from ..StiExcelExportSettings import StiExcelExportSettings
            return StiExcelExportSettings()
        
        if format == StiExportFormat.WORD:
            from ..StiWordExportSettings import StiWordExportSettings
            return StiWordExportSettings()
        
        if format == StiExportFormat.POWERPOINT:
            from ..StiPowerPointExportSettings import \
                StiPowerPointExportSettings
            return StiPowerPointExportSettings()
        
        if format == StiExportFormat.ODS:
            from ..StiOdsExportSettings import StiOdsExportSettings
            return StiOdsExportSettings()
        
        if format == StiExportFormat.ODT:
            from ..StiOdtExportSettings import StiOdtExportSettings
            return StiOdtExportSettings()
        
        if format == StiExportFormat.HTML:
            if reportType == StiReportType.DASHBOARD:
                from stimulsoft_dashboards.export import StiHtmlDashboardExportSettings
                return StiHtmlDashboardExportSettings()
            
            from ..StiHtmlExportSettings import StiHtmlExportSettings
            return StiHtmlExportSettings(StiHtmlType.HTML)
        
        if format == StiExportFormat.HTML5:
            from ..StiHtmlExportSettings import StiHtmlExportSettings
            return StiHtmlExportSettings(StiHtmlType.HTML5)
        
        if format == StiExportFormat.XML:
            from ..StiDataExportSettings import StiDataExportSettings
            return StiDataExportSettings(StiDataType.XML)
        
        if format == StiExportFormat.JSON:
            from ..StiDataExportSettings import StiDataExportSettings
            return StiDataExportSettings(StiDataType.JSON)
        
        if format == StiExportFormat.CSV:
            if reportType == StiReportType.DASHBOARD:
                from stimulsoft_dashboards.export import StiDataDashboardExportSettings
                return StiDataDashboardExportSettings()
            
            from ..StiDataExportSettings import StiDataExportSettings
            return StiDataExportSettings(StiDataType.CSV)
        
        if format == StiExportFormat.DIF:
            from ..StiDataExportSettings import StiDataExportSettings
            return StiDataExportSettings(StiDataType.DIF)
        
        if format == StiExportFormat.SYLK:
            from ..StiDataExportSettings import StiDataExportSettings
            return StiDataExportSettings(StiDataType.SYLK)
        
        if format == StiExportFormat.DBF:
            from ..StiDataExportSettings import StiDataExportSettings
            return StiDataExportSettings(StiDataType.DBF)
        
        if format == StiExportFormat.IMAGE_GIF:
            from ..StiImageExportSettings import StiImageExportSettings
            return StiImageExportSettings(StiImageType.GIF)
        
        if format == StiExportFormat.IMAGE_BMP:
            from ..StiImageExportSettings import StiImageExportSettings
            return StiImageExportSettings(StiImageType.BMP)
        
        if format == StiExportFormat.IMAGE_PNG:
            from ..StiImageExportSettings import StiImageExportSettings
            return StiImageExportSettings(StiImageType.PNG)
        
        if format == StiExportFormat.IMAGE_TIFF:
            from ..StiImageExportSettings import StiImageExportSettings
            return StiImageExportSettings(StiImageType.TIFF)
        
        if format == StiExportFormat.IMAGE_JPEG:
            from ..StiImageExportSettings import StiImageExportSettings
            return StiImageExportSettings(StiImageType.JPEG)
        
        if format == StiExportFormat.IMAGE_PCX:
            from ..StiImageExportSettings import StiImageExportSettings
            return StiImageExportSettings(StiImageType.PCX)
        
        if format == StiExportFormat.IMAGE_SVG:
            if reportType == StiReportType.DASHBOARD:
                from stimulsoft_dashboards.export import StiImageDashboardExportSettings
                return StiImageDashboardExportSettings()
            
            from ..StiImageExportSettings import StiImageExportSettings
            return StiImageExportSettings(StiImageType.SVG)
        
        if format == StiExportFormat.IMAGE_SVGZ:
            from ..StiImageExportSettings import StiImageExportSettings
            return StiImageExportSettings(StiImageType.SVGZ)
        
        from ..StiExportSettings import StiExportSettings
        return StiExportSettings()
    