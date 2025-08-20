from __future__ import annotations

import typing

from stimulsoft_data_adapters.classes.StiFunctions import StiFunctions

from ..classes.StiElement import StiElement
from ..enums.StiComponentType import StiComponentType

if typing.TYPE_CHECKING:
    from .StiComponent import StiComponent


class StiJavaScript(StiElement):

### Private

    __component: StiComponent = None
    __head: list = None


### Options

    usePacked = False
    
    reportsChart = True
    reportsExport = True
    reportsImportXlsx = True
    reportsMaps = True
    blocklyEditor = True

    @property
    def reportsSet(self) -> bool:
        """This option has been deprecated and is no longer used."""

        return self.reportsChart and self.reportsExport and self.reportsImportXlsx and self.reportsMaps and self.blocklyEditor
    
    @reportsSet.setter
    def reportsSet(self, value):
        pass
    

### Methods

    def appendHead(self, value: str):
        if not StiFunctions.isNullOrEmpty(value):
            self.__head.append(value)


### HTML

    def getHtml(self) -> str:
        """
        Gets the HTML representation of the component.
        
        return:
            Prepared JavaScript code for embedding in an HTML template in the HEAD section.
        """
        
        extension = 'pack.js' if (self.usePacked) else 'js'
        reportsSet = self.reportsChart and self.reportsExport and self.reportsImportXlsx and self.reportsMaps and self.blocklyEditor

        result = ''
        for value in self.__head:
            result += f'{value}\n'

        scripts: list = []
        if reportsSet:
            scripts.append(f'stimulsoft.reports.{extension}')
        else:
            scripts.append(f'stimulsoft.reports.engine.{extension}')
            if self.reportsChart:
                scripts.append(f'stimulsoft.reports.chart.{extension}')
            if self.reportsExport:
                scripts.append(f'stimulsoft.reports.export.{extension}')
            if self.reportsMaps:
                scripts.append(f'stimulsoft.reports.maps.{extension}')
            if self.reportsImportXlsx:
                scripts.append(f'stimulsoft.reports.import.xlsx.{extension}')

        if StiFunctions.isDashboardsProduct():
            scripts.append(f'stimulsoft.dashboards.{extension}')

        if self.__component.componentType == StiComponentType.VIEWER or self.__component.componentType == StiComponentType.DESIGNER:
            scripts.append(f'stimulsoft.viewer.{extension}')

        if self.__component.componentType == StiComponentType.DESIGNER:
            scripts.append(f'stimulsoft.designer.{extension}')

            if self.blocklyEditor:
                scripts.append(f'stimulsoft.blockly.editor.{extension}')

        scripts.append('stimulsoft.handler.js')

        url = self.__component.handler.url
        separator = '?' if url.find('?') < 0 else '&'
        result += '\n'.join([f'<script src="{url}{separator}sti_event=GetResource&sti_data={name}" type="text/javascript"></script>' for name in scripts])
        
        return result + '\n' + super().getHtml()
    

### Constructor

    def __init__(self, component: StiComponent):
        self.__component = component
        self.__head = []
