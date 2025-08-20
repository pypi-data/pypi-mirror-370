import base64

from stimulsoft_data_adapters.events.StiEventArgs import StiEventArgs
from stimulsoft_reports.enums import StiReportType

from ..export.enums.StiExportFormat import StiExportFormat
from ..export.StiExportSettings import StiExportSettings
from .enums.StiExportAction import StiExportAction


class StiExportEventArgs(StiEventArgs):

### Fields

    __action = StiExportAction.NONE
    __format = StiExportFormat.NONE
    __settings: StiExportSettings = None
    __fileExtension: str = None
    __mimeType: str = None
    __data: bytes = None


### Properties

    @property
    def action(self) -> StiExportAction:
        """[enum] The current action for which the report was exported."""

        return StiExportAction.EXPORT_REPORT if self.__action == StiExportAction.NONE else self.__action
    
    @action.setter
    def action(self, value: int):
        self.__action = value


    @property
    def format(self) -> StiExportFormat:
        """[enum] The current export format of the report."""

        return self.__format
    
    @format.setter
    def format(self, value: StiExportFormat):
        self.__format = value
        self.__fileExtension = StiExportFormat.getFileExtension(value)
        self.__mimeType = StiExportFormat.getMimeType(value)
        self.settings = self.__settings


    formatName: str = None
    """String name of the current export format of the report."""


    @property
    def settings(self) -> StiExportSettings:
        """The object of all settings for the current report export."""

        return self.__settings
    
    @settings.setter
    def settings(self, value):
        self.__settings = value
        if self.format != None and self.reportType != StiReportType.AUTO and isinstance(value, dict):
            self.__settings = StiExportFormat.getExportSettings(self.format, self.reportType)
            self.__settings.setObject(value)


    openAfterExport: bool = None
    """The flag indicates that the report will be exported in a new browser tab (True), or the file will be saved (False)."""


    fileName: str = None
    """The file name of the exported report."""


    @property
    def fileExtension(self) -> str:
        """The file extension for the current report export."""

        return self.__fileExtension


    @property
    def mimeType(self) -> str:
        """The MIME type for the current report export."""

        return self.__mimeType


    @property
    def data(self) -> bytes:
        """The byte data of the exported report."""

        return self.__data
    
    @data.setter
    def data(self, value: str):
        if value != None:
            self.__data = base64.b64decode(value)


    __reportType: StiReportType = StiReportType.AUTO

    @property
    def reportType(self) -> StiReportType:
        """[enum] The current type of report being exported."""

        return self.__reportType
    
    @reportType.setter
    def reportType(self, value):
        self.__reportType = value
        self.settings = self.__settings