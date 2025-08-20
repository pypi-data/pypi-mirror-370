import base64
import gzip
import os

from stimulsoft_data_adapters.classes.StiPath import StiPath

from ..classes.StiComponent import StiComponent
from ..classes.StiHandler import StiHandler
from ..classes.StiNodeJs import StiNodeJs
from ..classes.StiResult import StiResult
from ..enums.StiComponentType import StiComponentType
from ..enums.StiEventType import StiEventType
from ..enums.StiHtmlMode import StiHtmlMode
from ..events.StiComponentEvent import StiComponentEvent
from ..events.StiReportEventArgs import StiReportEventArgs
from ..export.enums.StiExportFormat import StiExportFormat
from ..export.StiDataExportSettings import StiDataExportSettings
from ..export.StiExportSettings import StiExportSettings
from ..export.StiHtmlExportSettings import StiHtmlExportSettings
from ..export.StiImageExportSettings import StiImageExportSettings
from .dictionary.StiDictionary import StiDictionary
from .enums.StiEngineType import StiEngineType
from .enums.StiRangeType import StiRangeType
from .StiPagesRange import StiPagesRange


class StiReport(StiComponent):

### Events

    @property
    def onBeforeRender(self) -> StiComponentEvent:
        """The event is invoked called before all actions related to report rendering. Only JavaScript functions are supported."""
        return self._getEvent('onBeforeRender')

    @onBeforeRender.setter
    def onBeforeRender(self, value):
        self._setEvent('onBeforeRender', value)
        

    @property
    def onAfterRender(self) -> StiComponentEvent:
        """The event is invoked called immediately after report rendering. Only JavaScript functions are supported."""
        return self._getEvent('onAfterRender')

    @onAfterRender.setter
    def onAfterRender(self, value):
        self._setEvent('onAfterRender', value)


### Fields

    __dictionary: StiDictionary = None
    __clearDataCalled = False
    __clearDataSourcesCalled = False
    __renderCalled = False
    __printCalled = False
    __exportCalled = False
    __openAfterExport = False

    __nodejs: StiNodeJs = None
    __reportDataName: str = None
    __reportData: object = None
    __reportDataSynchronization = False
    __reportString: str = None
    __reportFile: str = None
    __documentString: str = None
    __documentFile: str = None
    __exportFile: str = None
    __exportFormat: int = None
    __pageRange: str = None
    __exportSettings: StiExportSettings = None
    __error: str = None


### Events

    def __getBeforeRenderResult(self) -> StiResult:
        args = StiReportEventArgs(self.handler.request)
        if self.__reportData != None:
            args.regReportData(self.__reportDataName, self.__reportData, self.__reportDataSynchronization)

        result = self.onBeforeRender.getResult(args)
        if result != None and result.success:
            result.data = args.data

        return result

    def getEventResult(self) -> StiResult:
        if self.request.event == StiEventType.BEFORE_RENDER:
            return self.__getBeforeRenderResult()

        return super().getEventResult()


### Helpers

    def __clearReport(self) -> None:
        self.__reportString = None
        self.__reportFile = None
        self.__documentString = None
        self.__documentFile = None
        self.__exportFile = None

    def __clearError(self):
        self.__error = None
    
    def __loadReportFile(self, path: StiPath|str) -> str:
        path = path if isinstance(path, StiPath) else StiPath(path)
        if path.filePath != None:
            with open(path.filePath, mode='r', encoding='utf-8') as file:
                data = file.read()
                if path.fileExtension == 'mrz' or path.fileExtension == 'mdz':
                    return data
                
                buffer = gzip.compress(data.encode())
                return base64.b64encode(buffer).decode()
        
        return None
    
    def __saveReportFile(self, path: StiPath|str, extension: str, data: bytes) -> bool:
        path = path if isinstance(path, StiPath) else StiPath(path)
        if path.directoryPath != None:
            path.fileName = path.fileName or (self.__exportFile or 'Report') + '.' + extension
            filePath = os.path.join(path.directoryPath, path.fileName)
            with open(filePath, mode='wb') as file:
                file.write(data)
                file.close()
                return True
        
        return False
    

### Properties

    engine = StiEngineType.CLIENT_JS
    """Gets or sets the report building and export mode - on the client side in a browser window or on the server side using Node.js"""

    @property
    def componentType(self) -> StiComponentType:
        return StiComponentType.REPORT
    
    @property
    def dictionary(self) -> StiDictionary:
        """Gets a report data dictionary that allows you to add new variables to an existing report."""

        return self.__dictionary
    
    @property
    def nodejs(self) -> StiNodeJs:
        """
        Gets the Node.js engine, used to build and export reports on the server side.
        Contains the necessary deployment and operation settings.
        """

        if self.__nodejs == None:
            self.__nodejs = StiNodeJs(self)

        return self.__nodejs
    
    @property
    def error(self) -> str:
        """Main text of the last error."""

        return self.__error
    

### HTML

    def __getLoadReportHtml(self) -> str:
        if len(self.__documentFile or '') > 0:
            return f"{self.id}.loadDocumentFile('{self.__documentFile}');\n"

        elif len(self.__documentString or '') > 0:
            return f"{self.id}.loadPackedDocument('{self.__documentString}');\n"
        
        elif len(self.__reportFile or '') > 0:
            return f"{self.id}.loadFile('{self.__reportFile}');\n"

        elif len(self.__reportString or '') > 0:
            return f"{self.id}.loadPacked('{self.__reportString}');\n"
        
        return ''
    
    def __getNodeJsOutput(self, type, data) -> str:
        return f"console.log('{self.nodejs.id}{{\"type\":\"{type}\", \"data\":\"' + {data} + '\"}}{self.nodejs.id}');"
    
    def __getPrintHtml(self) -> str:
        if self.__printCalled:
            pageRange = self.__pageRange
            pageRangeHtml = ''
            pageRangeId = ''

            if self.__pageRange != None:
                if not isinstance(pageRange, StiPagesRange) and len(str(pageRange)) > 0:
                    pageRange = StiPagesRange(StiRangeType.PAGES, str(pageRange))
                
                pageRangeHtml = pageRange.getHtml()
                pageRangeId = pageRange.id

            return f'{pageRangeHtml}{self.id}.print({pageRangeId});\n'
        
        return ''
    
    def __getExportHtml(self) -> str:
        result = ''
        if self.__exportCalled:
            exportFileExt = StiExportFormat.getFileExtension(self.__exportFormat, self.__exportSettings)
            exportMimeType = StiExportFormat.getMimeType(self.__exportFormat, self.__exportSettings)
            exportName = StiExportFormat.getFormatName(self.__exportFormat)

            result = self.__exportSettings.getHtml() if self.__exportSettings != None and not self.__exportSettings.htmlRendered else 'let settings = null;\n'
            result += f'{self.id}.exportDocumentAsync(function (data) {{\n'
            if self.engine == StiEngineType.SERVER_NODE_JS:
                result += 'let buffer = Buffer.from(data);\n' + self.__getNodeJsOutput('bytes', "buffer.toString('base64')") + '\n'
            else:
                result += \
                    f"let blob = new Blob([new Uint8Array(data)], {{type: '{exportMimeType}'}});\nlet fileURL = URL.createObjectURL(blob);\nwindow.open(fileURL);\n" \
                    if self.__openAfterExport else \
                    f"Stimulsoft.System.StiObject.saveAs(data, '{self.__exportFile}.{exportFileExt}', '{exportMimeType}');\n"
            result += f'}}, Stimulsoft.Report.StiExportFormat.{exportName}, null, settings);\n'
        
        return result
    
    def __getAfterRenderHtml(self) -> str:
        result = self.__getPrintHtml()
        result += self.__getExportHtml()

        return result
    
    def __getAfterRenderNodeHtml(self) -> str:
        return f"let {self.id}String = {self.id}.savePackedDocumentToString();\n" + self.__getNodeJsOutput('string', f'{self.id}String')

    def _getComponentHtml(self) -> str:
        result = super()._getComponentHtml()

        result += f'let {self.id} = new Stimulsoft.Report.StiReport();\n'
        
        result += self.onPrepareVariables.getHtml(True)
        result += self.onBeginProcessData.getHtml(True)
        result += self.onEndProcessData.getHtml(process = False)
        result += self.__getLoadReportHtml()
        result += self.dictionary.getHtml()
        result += self.onBeforeRender.getHtml(True, internal = True)

        if self.__clearDataCalled:
            result += f'{self.id}.dictionary.databases.clear()\n'

        if self.__clearDataSourcesCalled:
            result += f'{self.id}.dictionary.dataSources.clear()\n'

        if self.__renderCalled:
            renderAsyncHtml = f'{self.id}.renderAsync(function () {{\n'
            renderAsyncHtml += self.onAfterRender.getHtml(internal = True)
            renderAsyncHtml += self.__getAfterRenderHtml()
            renderAsyncHtml += f'}});\n'

            result += \
                self._getBeforeRenderCallback(renderAsyncHtml) \
                if self.onBeforeRender.hasServerCallbacks() else \
                renderAsyncHtml
        else:
            result += self.__getAfterRenderHtml()

        return result
    

### Load / Save

    def loadFile(self, filePath: str, load = False) -> None:
        """
        Loads a report template from a file or URL address.

        filePath:
            The path to the .mrt file or the URL of the report template.

        load:
            Loads a report file on the server side into report object.
        """
    
        self.__clearReport()
        path = StiPath(filePath)
        self.__exportFile = path.fileNameOnly

        if load: self.__reportString = self.__loadReportFile(path)
        else: self.__reportFile = filePath if len(filePath or '') == 0 else filePath.replace('\\', '/')

    def load(self, data: str, fileName: str = 'Report') -> None:
        """
        Loads a report template from an XML or JSON string and store it as a packed string in Base64 format.

        data:
            Report template in XML or JSON format.

        fileName:
            The name of the report file to be used for saving and exporting.
        """

        self.__clearReport()
        self.__exportFile = fileName
        gzipBytes = gzip.compress(data.encode())
        self.__reportString = base64.b64encode(gzipBytes).decode()

    def loadPacked(self, data: str, fileName = 'Report') -> None:
        """
        Loads a report template from a packed string in Base64 format.

        data:
            Report template as a packed string in Base64 format.

        fileName:
            The name of the report file to be used for saving and exporting.
        """
    
        self.__clearReport()
        self.__exportFile = fileName
        self.__reportString = data
    
    def loadDocumentFile(self, filePath: str, load = False) -> None:
        """
        Loads a rendered report from a file or URL address.

        filePath:
            The path to the .mdc file or the URL of the rendered report.

        load:
            Loads a report file on the server side into report object.
        """

        self.__clearReport()
        path = StiPath(filePath)
        self.__exportFile = path.fileNameOnly

        if load: self.__documentString = self.__loadReportFile(path)
        else: self.__documentFile = filePath if len(filePath or '') == 0 else filePath.replace('\\', '/')

    def loadDocument(self, data: str, fileName = 'Report') -> None:
        """
        Loads a rendered report from an XML or JSON string and send it as a packed string in Base64 format.

        data:
            Rendered report in XML or JSON format.

        fileName:
            The name of the report file to be used for saving and exporting.
        """
    
        self.__clearReport()
        self.__exportFile = fileName
        gzipBytes = gzip.compress(data.encode())
        self.__documentString = base64.b64encode(gzipBytes).decode()

    def loadPackedDocument(self, data: str, fileName = 'Report') -> None:
        """
        Loads a rendered report from a packed string in Base64 format.

        data:
            Rendered report as a packed string in Base64 format.

        fileName:
            The name of the report file to be used for saving and exporting.
        """
    
        self.__clearReport()
        self.__exportFile = fileName
        self.__documentString = data

    def saveDocument(self, filePath: str = None) -> str|bool:
        """
        Saves a rendered report in JSON format.

        filePath:
            The path to the .mdc file of the rendered report.

        return:
            The result of saving the report. If property 'filePath' not specified, the function will return JSON string of the report.
        """

        if len(self.__documentString or '') > 0:
            data = gzip.decompress(base64.b64decode(self.__documentString))
            return data.decode() if len(filePath or '') == 0 else self.__saveReportFile(filePath, 'mdc', data)
        
        return False

    def savePackedDocument(self, filePath: str = None) -> str|bool:
        """
        Saves a rendered report as packed string in Base64 format.

        filePath:
            The path to the .mdz file of the rendered report.

        return:
            The result of saving the report. If property 'filePath' not specified, the function will return Base64 string of the report.
        """

        if len(self.__documentString or '') > 0:
            if len(filePath or '') == 0:
                return self.__documentString
            
            data = base64.b64decode(self.__documentString)
            return self.__saveReportFile(filePath, 'mdz', data)
            
        return False
        

### Process

    def clearData(self, clearDataSources = False):
        """
        Clears all data connections in the report before rendering it. By default, the data sources will not be cleared.

        clearDataSources:
            If true, all data sources in the dictionary will be completely deleted.
        """

        self.__clearDataCalled = True
        self.__clearDataSourcesCalled = clearDataSources

    def regData(self, name: str, data: object, synchronize = False):
        """
        Sets the data that will be passed to the report generator before building the report.
        It can be an XML or JSON string, as well as an array or a data object that will be serialized into a JSON string.
        
        name:
            The name of the data source in the report.

        data:
            Report data as a string, array, or object.

        synchronize:
            If true, data synchronization will be called after the data is registered.
        """
        
        self.__reportDataName = name
        self.__reportData = data
        self.__reportDataSynchronization = synchronize

        if not self.onBeforeRender.hasServerCallbacks():
            self.onBeforeRender += True

    def render(self) -> bool:
        """
        Builds a report, or prepares the necessary JavaScript to build the report.
        
        return:
            The result of building a report.
        """
   
        self.__clearError()
        self.__renderCalled = True

        if self.engine == StiEngineType.SERVER_NODE_JS:
            self._setHtmlRendered(False)
            afterRenderScript = self.__getAfterRenderNodeHtml()
            self.onAfterRender += afterRenderScript
            script = self.getHtml(StiHtmlMode.SCRIPTS)
            self.onAfterRender -= afterRenderScript
            self.__renderCalled = False
            
            result = self.nodejs.run(script)
            if result == False:
                return False
            
            self.__documentString = result

        return True

    def print(self, pageRange: StiPagesRange|str|int = None) -> None:
        """
        Prepares the necessary JavaScript to print the report. The browser print dialog will be called.
        
        pagesRande:
            The page range or the page number to print.
        """
    
        self.__printCalled = True
        self.__pageRange = pageRange

    def exportDocument(self, format: StiExportFormat, settings: StiExportSettings = None, openAfterExport = False, filePath: str = None) -> bytes|bool:
        """
        Exports the rendered report to the specified format, or prepares the necessary JavaScript to export the report.

        Important! The export function does not automatically build the report template.

        format:
            [enum] Report export format.

        settings:
            Export settings, the type of settings must match the export format.
        
        openAfterExport:
            Automatically open the exported report in a browser window if the export is performed on the client side.

        filePath:
            The path to the file of the exported document. It only works with server-side Node.js mode.

        return:
            Byte data of the exported report, or the boolean result of the export.
        """
    
        self.__clearError()
        self.__exportCalled = True
        self.__openAfterExport = openAfterExport
        self.__exportFormat = format

        self.__exportSettings = settings
        if settings != None:
            if isinstance(settings, StiHtmlExportSettings) and settings.htmlType == None:
                settings.setHtmlType(format)

            if isinstance(settings, StiDataExportSettings) and settings.dataType == None:
                settings.setDataType(format)

            if isinstance(settings, StiImageExportSettings) and settings.imageType == None:
                settings.setImageType(format)
                
            self.__exportFormat = settings.getExportFormat()

        if self.engine == StiEngineType.SERVER_NODE_JS:
            self._setHtmlRendered(False)
            script = self.getHtml(StiHtmlMode.SCRIPTS)
            self.__exportCalled = False
            result = self.nodejs.run(script)
            
            if result and len(filePath or '') > 0:
                extension = StiExportFormat.getFileExtension(format, settings)
                result = self.__saveReportFile(filePath, extension, result)
                if not result:
                    self.__error = f"An error occurred while writing \"{filePath}\" file."
            
            return result
        
        return True
    

### Constructor

    def __init__(self):
        super().__init__()

        self.id = 'report'
        self.__dictionary = StiDictionary(self)
        self.handler = StiHandler()