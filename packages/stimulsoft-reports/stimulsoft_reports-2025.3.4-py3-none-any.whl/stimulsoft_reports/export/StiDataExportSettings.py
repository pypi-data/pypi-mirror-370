from ..enums.Encoding import Encoding
from .enums.StiDataExportMode import StiDataExportMode
from .enums.StiDataType import StiDataType
from .enums.StiDbfCodePages import StiDbfCodePages
from .enums.StiExportFormat import StiExportFormat
from .StiExportSettings import StiExportSettings


class StiDataExportSettings(StiExportSettings):
    """Class describes settings for export to data formats."""

### Properties

    dataType: StiDataType = None
    """[enum] Gets or sets type of the exported data file."""

    dataExportMode = StiDataExportMode.DATA
    """[enum] Gets or sets data export mode. SYLK and DIF formats does not support this property."""

    encoding = Encoding.UTF8
    """[enum] Gets or sets encoding of DIF file format. XML, JSON and DBF formats does not support this property."""

    exportDataOnly = False
    """Gets or sets value which indicates that all formatting of exported report will be removed. XML, JSON, DBF and CSV formats does not support this property."""

    codePage = StiDbfCodePages.DEFAULT
    """[enum] Gets or sets code page of DBF file format. DBF format only!"""

    separator = ';'
    """Gets or sets string which represents column separator in CSV file. CSV format only!"""

    tableName: str = None
    """Gets or sets name of the table. XML and JSON formats only!"""

    skipColumnHeaders = False
    """Gets or sets value which indicates that export engine will be write column headers as column headers in table or as simple column values. CSV format only!"""

    useDefaultSystemEncoding = True
    """Gets or sets value which indicates that default system encoding will be used for DIF and SYLK formats. DIF and SYLK format only!"""


### Helpers

    def getExportFormat(self):
        if self.dataType == StiDataType.DBF:
            return StiExportFormat.DBF
        
        if self.dataType == StiDataType.DIF:
            return StiExportFormat.DIF
        
        if self.dataType == StiDataType.SYLK:
            return StiExportFormat.SYLK
        
        if self.dataType == StiDataType.XML:
            return StiExportFormat.XML
        
        if self.dataType == StiDataType.JSON:
            return StiExportFormat.JSON
        
        return StiExportFormat.CSV
    
    def setDataType(self, format = None):
        if format == None:
            format = self.getExportFormat()
            
        if format == StiExportFormat.DBF:
            self.dataType = StiDataType.DBF

        elif format == StiExportFormat.DIF:
            self.dataType = StiDataType.DIF

        elif format == StiExportFormat.SYLK:
            self.dataType = StiDataType.SYLK

        elif format == StiExportFormat.XML:
            self.dataType = StiDataType.XML

        elif format == StiExportFormat.JSON:
            self.dataType = StiDataType.JSON

        elif format == StiExportFormat.CSV:
            self.dataType = StiDataType.CSV


### HTML

    def getHtml(self) -> str:
        self.setDataType()

        return super().getHtml()
    

### Constructor

    def __init__(self, dataType: StiDataType = None):
        """
        dataType:
            [enum] Type of the exported data file.
        """

        super().__init__()
        self.dataType = dataType