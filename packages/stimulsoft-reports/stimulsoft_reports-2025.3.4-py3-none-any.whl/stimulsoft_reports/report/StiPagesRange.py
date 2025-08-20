from ..classes.StiJsElement import StiJsElement
from .enums.StiRangeType import StiRangeType


class StiPagesRange(StiJsElement):
    """Class describes pages range."""

### Properties
    
    rangeType = StiRangeType.ALL
    """Gets type of pages range."""

    pageRanges = ''
    """Gets range of pages."""

    currentPage = 0
    """Gets current page."""


### Methods: HTML

    def getHtml(self, newPagesRange = True) -> str:
        result = f'let {self.id} = new Stimulsoft.Report.StiPagesRange();\n' if newPagesRange else ''
        if self.rangeType != StiRangeType.ALL:
            result += f'{self.id}.rangeType = {self.rangeType.value};\n'

            if len(self.pageRanges or '') > 0:
                result += f"{self.id}.pageRanges = '{self.pageRanges}';\n"

            if self.currentPage > 0:
                result += f'{self.id}.currentPage = {self.currentPage};\n'

        return result + super().getHtml()
    

### Constructor

    def __init__(self, rangeType = StiRangeType.ALL, pageRanges = '', currentPage = 0) -> None:
        self.id = 'pagesRange'
        self.rangeType = StiRangeType(rangeType) if isinstance(rangeType, int) else rangeType
        self.pageRanges = pageRanges
        self.currentPage = currentPage
