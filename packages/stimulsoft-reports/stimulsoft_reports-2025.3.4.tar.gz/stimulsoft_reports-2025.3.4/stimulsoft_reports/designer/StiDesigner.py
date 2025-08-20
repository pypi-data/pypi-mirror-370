from ..classes.StiComponent import StiComponent
from ..classes.StiHandler import StiHandler
from ..classes.StiResult import StiResult
from ..enums.StiComponentType import StiComponentType
from ..enums.StiEventType import StiEventType
from ..enums.StiHtmlMode import StiHtmlMode
from ..events.StiComponentEvent import StiComponentEvent
from ..events.StiReportEventArgs import StiReportEventArgs
from ..report.StiReport import StiReport
from .options.StiDesignerOptions import StiDesignerOptions


class StiDesigner(StiComponent):
    
### Events

    @property
    def onAfterInitialize(self) -> StiComponentEvent:
        """The event is invoked after the JavaScript component is initialized. Only JavaScript functions are supported."""
        return self._getEvent('onAfterInitialize')

    @onAfterInitialize.setter
    def onAfterInitialize(self, value):
        self._setEvent('onAfterInitialize', value)

    @property
    def onCreateReport(self) -> StiComponentEvent:
        """The event is invoked after creation a new report in the designer. Python and JavaScript functions are supported."""
        return self._getEvent('onCreateReport')

    @onCreateReport.setter
    def onCreateReport(self, value):
        self._setEvent('onCreateReport', value)
        

    @property
    def onOpenReport(self) -> StiComponentEvent:
        """The event is invoked before opening a report from the designer menu after clicking the button. Only JavaScript functions are supported."""
        return self._getEvent('onOpenReport')

    @onOpenReport.setter
    def onOpenReport(self, value):
        self._setEvent('onOpenReport', value)
        

    @property
    def onOpenedReport(self) -> StiComponentEvent:
        """The event is invoked after opening a report before sending to the designer. Python and JavaScript functions are supported."""
        return self._getEvent('onOpenedReport')

    @onOpenedReport.setter
    def onOpenedReport(self, value):
        self._setEvent('onOpenedReport', value)
        

    @property
    def onSaveReport(self) -> StiComponentEvent:
        """The event is invoked when saving a report in the designer. Python and JavaScript functions are supported."""
        return self._getEvent('onSaveReport')

    @onSaveReport.setter
    def onSaveReport(self, value):
        self._setEvent('onSaveReport', value)
        

    @property
    def onSaveAsReport(self) -> StiComponentEvent:
        """The event is invoked when saving a report in the designer with a preliminary input of the file name. Python and JavaScript functions are supported."""
        return self._getEvent('onSaveAsReport')

    @onSaveAsReport.setter
    def onSaveAsReport(self, value):
        self._setEvent('onSaveAsReport', value)
        

    @property
    def onPreviewReport(self) -> StiComponentEvent:
        """The event is invoked when going to the report view tab. Python and JavaScript functions are supported."""
        return self._getEvent('onPreviewReport')

    @onPreviewReport.setter
    def onPreviewReport(self, value):
        self._setEvent('onPreviewReport', value)


    @property
    def onCloseReport(self) -> StiComponentEvent:
        """The event is invoked after the report is closed in the designer. Python and JavaScript functions are supported."""
        return self._getEvent('onCloseReport')

    @onCloseReport.setter
    def onCloseReport(self, value):
        self._setEvent('onCloseReport', value)
        

    @property
    def onExit(self) -> StiComponentEvent:
        """The event is invoked when by clicking the Exit button in the main menu of the designer. Only JavaScript functions are supported."""
        return self._getEvent('onExit')

    @onExit.setter
    def onExit(self, value):
        self._setEvent('onExit', value)


### Fields

    __options: StiDesignerOptions = None
    __report: StiReport = None


### Properties

    @property
    def componentType(self) -> StiComponentType:
        return StiComponentType.DESIGNER

    @property
    def report(self) -> StiReport:
        """Gets or sets a report object for the designer."""

        return self.__report
    
    @report.setter
    def report(self, value: StiReport):
        self.__report = value
        if value != None:
            value._setEventsFrom(self)
            value.handler = self.handler
            value.license = self.license
            value.fontCollection = self.fontCollection
            value.functions = self.functions
    
    @property
    def options(self) -> StiDesignerOptions:
        """All designer component options, divided by categories."""

        return self.__options
    
    @options.setter
    def options(self, value: StiDesignerOptions):
        if value != None:
            value.component = self
            self.__options = value


### Event handlers

    def __getCreateReportResult(self) -> StiResult:
        args = StiReportEventArgs(self.handler.request)
        result = self.onCreateReport.getResult(args)
        if result != None and args.report != self.handler.request.report:
            result.report = args.report

        return result
    
    def __getOpenedReportResult(self) -> StiResult:
        args = StiReportEventArgs(self.handler.request)
        return self.onOpenedReport.getResult(args)

    def __getSaveReportResult(self) -> StiResult:
        args = StiReportEventArgs(self.handler.request)
        return self.onSaveReport.getResult(args)
    
    def __getSaveAsReportResult(self) -> StiResult:
        args = StiReportEventArgs(self.handler.request)
        return self.onSaveAsReport.getResult(args)
    
    def __getPreviewReportResult(self) -> StiResult:
        args = StiReportEventArgs(self.handler.request)
        result = self.onPreviewReport.getResult(args)
        if result != None and args.report != self.handler.request.report:
            result.report = args.report

        return result
    
    def __getCloseReportResult(self) -> StiResult:
        args = StiReportEventArgs(self.handler.request)
        return self.onCloseReport.getResult(args)

    def getEventResult(self) -> StiResult:
        if self.request.event == StiEventType.CREATE_REPORT:
            return self.__getCreateReportResult()
        
        if self.request.event == StiEventType.OPENED_REPORT:
            return self.__getOpenedReportResult()
        
        if self.request.event == StiEventType.SAVE_REPORT:
            return self.__getSaveReportResult()
        
        if self.request.event == StiEventType.SAVE_AS_REPORT:
            return self.__getSaveAsReportResult()
        
        if self.request.event == StiEventType.PREVIEW_REPORT:
            return self.__getPreviewReportResult()
        
        if self.request.event == StiEventType.CLOSE_REPORT:
            return self.__getCloseReportResult()

        if self.report != None:
            return self.report.getEventResult()
        
        return super().getEventResult()


### HTML

    def _getComponentHtml(self) -> str:
        result = super()._getComponentHtml()

        result += self.options.getHtml()
        result += f"let {self.id} = new Stimulsoft.Designer.StiDesigner({self.options.id}, '{self.id}', false);\n"

        result += self.onPrepareVariables.getHtml(True)
        result += self.onBeginProcessData.getHtml(True)
        result += self.onEndProcessData.getHtml()
        result += self.onCreateReport.getHtml(True)
        result += self.onOpenReport.getHtml()
        result += self.onOpenedReport.getHtml()
        result += self.onSaveReport.getHtml(False, True)
        result += self.onSaveAsReport.getHtml(False, True)
        result += self.onPreviewReport.getHtml(True)
        result += self.onCloseReport.getHtml(True)
        result += self.onExit.getHtml(False, False, False)

        if self.report != None:
            if not self.report.htmlRendered:
                result += self.report.getHtml(StiHtmlMode.SCRIPTS)

            assignHtml = f'{self.id}.report = {self.report.id};\n'
            result += \
                self._getBeforeRenderCallback(assignHtml) \
                if self.report.onBeforeRender.hasServerCallbacks() else \
                assignHtml
            
        result += f"{self.id}.renderHtml('{self.id}Content');\n"
        result += self.onAfterInitialize.getHtml(False, False, False, True)

        return result

    def getHtml(self, mode = StiHtmlMode.HTML_SCRIPTS) -> str:
        if mode == StiHtmlMode.HTML_PAGE:
            self.options.appearance.fullScreenMode = True
    
        return super().getHtml(mode)
    

### Constructor

    def __init__(self):
        super().__init__()

        self.id = 'designer'
        self.options = StiDesignerOptions()
        self.handler = StiHandler()