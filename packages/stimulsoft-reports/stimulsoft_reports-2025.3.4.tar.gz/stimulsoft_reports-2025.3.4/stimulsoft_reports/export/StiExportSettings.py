from __future__ import annotations

import typing
from enum import Enum

from ..classes.StiJsElement import StiJsElement
from .enums.StiExportFormat import StiExportFormat

if typing.TYPE_CHECKING:
    from ..report.StiPagesRange import StiPagesRange


class StiExportSettings(StiJsElement):

### Fields

    __pageRange: StiPagesRange = None


### Properties

    @property
    def pageRange(self) -> StiPagesRange:
        return self.__pageRange
    
    @pageRange.setter
    def pageRange(self, value: StiPagesRange):
        if value == None:
            value = StiPagesRange()
        
        value.id = f"{self.id}.pageRange"
        self.__pageRange = value


### Helpers
    
    def _getStringValue(self, name: str, value) -> str:
        if isinstance(value, Enum) and name == 'encoding':
            return f'eval("{value.value}")'
        
        return super()._getStringValue(name, value)

    def getExportFormat(self):
        return StiExportFormat.NONE
    

### HTML

    def getHtml(self) -> str:
        result = f'let {self.id} = new Stimulsoft.Report.Export.{self.__class__.__name__}();\n'

        from ..report.StiPagesRange import StiPagesRange
        properties = self._getProperties()
        for name in properties:
            value = getattr(self, name)
            if getattr(type(self), name) != value:
                if isinstance(value, StiPagesRange):
                    result += value.getHtml(False)
                else:
                    jsvalue = self._getStringValue(name, value)
                    result += f'{self.id}.{name} = {jsvalue};\n'

        return result + super().getHtml()
    

### Constructor

    def __init__(self):
        self.id = 'settings'

        from ..report.StiPagesRange import StiPagesRange
        self.pageRange = StiPagesRange()