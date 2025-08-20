from .enums.StiDataExportMode import StiDataExportMode
from .enums.StiExcelRestrictEditing import StiExcelRestrictEditing
from .enums.StiExcelType import StiExcelType
from .enums.StiExportFormat import StiExportFormat
from .enums.StiImageFormat import ImageFormat
from .StiExportSettings import StiExportSettings


class StiExcelExportSettings(StiExportSettings):
    """Class describes settings for export to Microsoft Excel formats."""

### Properties

    excelType = StiExcelType.EXCEL_2007
    """[enum]"""

    useOnePageHeaderAndFooter = False
    """Gets or sets value which indicates that one (first) page header and page footer from report will be used in excel file."""

    @property
    def exportDataOnly(self) -> bool:
        """Gets or sets value which indicates that only data information will be created in excel file."""

        return self.dataExportMode != StiDataExportMode.ALL_BANDS

    @exportDataOnly.setter
    def exportDataOnly(self, value: bool):
        self.dataExportMode = StiDataExportMode.DATA | StiDataExportMode.HEADERS if value else StiDataExportMode.ALL_BANDS
    
    dataExportMode = StiDataExportMode.ALL_BANDS
    """[enum] Gets or sets data export mode."""

    exportPageBreaks = False
    """Gets or sets value which indicates that special page break markers will be created in excel file."""

    exportObjectFormatting = True
    """Gets or sets value which indicates that formatting of components will be exported to excel file or not."""

    exportEachPageToSheet = False
    """Gets or sets value which indicates that each page from report will be exported to excel file as separate excel sheet."""

    imageQuality = 0.75
    """Gets or sets image quality of images which will be exported to excel file."""

    imageResolution = 100
    """Gets or sets image resolution of images which will be exported to excel file."""

    imageFormat: ImageFormat = None
    """[enum] Gets or sets image format for exported images. 'None' corresponds to automatic mode."""

    companyString = 'Stimulsoft'
    """Gets or sets information about the creator to be inserted into result Excel file. ExcelXml is not supported!"""

    lastModifiedString: str = None

    restrictEditing = StiExcelRestrictEditing.NO
    """[enum]"""

    protectionPassword = '*TestPassword*'

    encryptionPassword: str = None


### Helpers

    def getExportFormat(self):
        return StiExportFormat.EXCEL