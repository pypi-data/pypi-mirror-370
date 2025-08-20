from stimulsoft_reports.report import StiPagesRange
from .StiReportEventArgs import StiReportEventArgs
from .enums.StiPrintAction import StiPrintAction


class StiPrintEventArgs(StiReportEventArgs):
    
### Fields

    __pageRange: StiPagesRange = None


### Properties

    printAction = StiPrintAction.NONE
    """[enum] The current print type of the report."""


    @property
    def pageRange(self) -> StiPagesRange:
        """The page range to print the report."""

        return self.__pageRange
    
    @pageRange.setter
    def pageRange(self, value: dict):
        self.__pageRange = StiPagesRange(value.get('rangeType'), value.get('pageRanges'), value.get('currentPage'))
