import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..classes.StiComponent import StiComponent
from ..classes.StiEmailSettings import StiEmailSettings
from ..classes.StiHandler import StiHandler
from ..classes.StiResult import StiResult
from ..enums.StiComponentType import StiComponentType
from ..enums.StiEventType import StiEventType
from ..enums.StiHtmlMode import StiHtmlMode
from ..events import StiPrintEventArgs
from ..events.StiComponentEvent import StiComponentEvent
from ..events.StiReportEventArgs import StiReportEventArgs
from ..report.StiReport import StiReport
from .options.StiViewerOptions import StiViewerOptions


class StiViewer(StiComponent):

### Events

    @property
    def onAfterInitialize(self) -> StiComponentEvent:
        """The event is invoked after the JavaScript component is initialized. Only JavaScript functions are supported."""
        return self._getEvent('onAfterInitialize')

    @onAfterInitialize.setter
    def onAfterInitialize(self, value):
        self._setEvent('onAfterInitialize', value)

    @property
    def onOpenReport(self) -> StiComponentEvent:
        """The event is invoked before opening a report from the viewer toolbar after clicking the button. Only JavaScript functions are supported."""
        return self._getEvent('onOpenReport')

    @onOpenReport.setter
    def onOpenReport(self, value):
        self._setEvent('onOpenReport', value)


    @property
    def onOpenedReport(self) -> StiComponentEvent:
        """The event is invoked after opening a report before showing. Python and JavaScript functions are supported."""
        return self._getEvent('onOpenedReport')

    @onOpenedReport.setter
    def onOpenedReport(self, value):
        self._setEvent('onOpenedReport', value)


    @property
    def onPrintReport(self) -> StiComponentEvent:
        """The event is invoked before printing a report. Python and JavaScript functions are supported."""
        return self._getEvent('onPrintReport')

    @onPrintReport.setter
    def onPrintReport(self, value):
        self._setEvent('onPrintReport', value)


    @property
    def onBeginExportReport(self) -> StiComponentEvent:
        """The event is invoked before exporting a report after the dialog of export settings. Python and JavaScript functions are supported."""
        return self._getEvent('onBeginExportReport')

    @onBeginExportReport.setter
    def onBeginExportReport(self, value):
        self._setEvent('onBeginExportReport', value)


    @property
    def onEndExportReport(self) -> StiComponentEvent:
        """The event is invoked after exporting a report till its saving as a file. Python and JavaScript functions are supported."""
        return self._getEvent('onEndExportReport')

    @onEndExportReport.setter
    def onEndExportReport(self, value):
        self._setEvent('onEndExportReport', value)


    @property
    def onInteraction(self) -> StiComponentEvent:
        """The event is invoked while interactive action of the viewer (dynamic sorting, collapsing, drill-down, applying of parameters)
        until processing values by the report generator. Only JavaScript functions are supported."""
        return self._getEvent('onInteraction')

    @onInteraction.setter
    def onInteraction(self, value):
        self._setEvent('onInteraction', value)


    @property
    def onEmailReport(self) -> StiComponentEvent:
        """The event is invoked after exporting a report before sending it by Email. Python and JavaScript functions are supported."""
        return self._getEvent('onEmailReport')

    @onEmailReport.setter
    def onEmailReport(self, value):
        self._setEvent('onEmailReport', value)


    @property
    def onDesignReport(self) -> StiComponentEvent:
        """The event occurs when clicking on the Design button in the viewer toolbar. Only JavaScript functions are supported."""
        return self._getEvent('onDesignReport')

    @onDesignReport.setter
    def onDesignReport(self, value):
        self._setEvent('onDesignReport', value)
    

### Fields

    __options: StiViewerOptions = None
    __report: StiReport = None


### Properties

    @property
    def componentType(self) -> StiComponentType:
        return StiComponentType.VIEWER

    @property
    def report(self) -> StiReport:
        """Gets or sets a report object for the viewer."""

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
    def options(self) -> StiViewerOptions:
        """All viewer component options, divided by categories."""

        return self.__options
    
    @options.setter
    def options(self, value: StiViewerOptions):
        if value != None:
            value.component = self
            self.__options = value


### Event handlers
    
    def __getOpenedReportResult(self) -> StiResult:
        args = StiReportEventArgs(self.handler.request)
        result = self.onOpenedReport.getResult(args)
        if result != None and args.report != self.handler.request.report:
            result.report = args.report

        return result

    def __getPrintReportResult(self) -> StiResult:
        args = StiPrintEventArgs(self.handler.request)
        result = self.onPrintReport.getResult(args)
        if result != None:
            if args.report != self.handler.request.report:
                result.report = args.report

            if args.pageRange != None:
                pageRange = args.pageRange.getObject()
                if pageRange != self.handler.request.pageRange:
                    result.pageRange = pageRange

        return result

    def __getBeginExportReportResult(self) -> StiResult:
        from ..events.StiExportEventArgs import StiExportEventArgs
        args = StiExportEventArgs(self.handler.request)
        result = self.onBeginExportReport.getResult(args)
        if result != None:
            if args.fileName != self.handler.request.fileName:
                result.fileName = args.fileName

            if args.settings != None:
                settings = args.settings.getObject()
                if settings != self.handler.request.settings:
                    result.settings = settings
        
        return result
    
    def __getEndExportReportResult(self) -> StiResult:
        from ..events.StiExportEventArgs import StiExportEventArgs
        args = StiExportEventArgs(self.handler.request)
        return self.onEndExportReport.getResult(args)
    
    """
    def __getInteractionResult(self) -> StiResult:
        args = StiReportEventArgs(self.handler.request)
        return self.onInteraction.getResult(args)
    """
    
    def __getEmailReportResult(self) -> StiResult:
        from ..events.StiEmailEventArgs import StiEmailEventArgs
        args = StiEmailEventArgs(self.handler.request)

        settings = StiEmailSettings()
        settings.toAddr = args.settings['email']
        settings.subject = args.settings['subject']
        settings.message = args.settings['message']
        settings.attachmentName = args.fileName if args.fileName.endswith('.' + args.fileExtension) else args.fileName + '.' + args.fileExtension

        args.settings = settings
        result = self.onEmailReport.getResult(args)
        if result == None or result.success == False:
            return result
            
        settings = args.settings

        part1 = MIMEText(settings.message, 'plain')
        part2 = MIMEBase('application', 'octet-stream')
        part2.set_payload(args.data)
        encoders.encode_base64(part2)
        part2.add_header('Content-Disposition', f'attachment; filename={settings.attachmentName}')
        
        message = MIMEMultipart('alternative')
        message['Subject'] = settings.subject
        message['From'] = settings.fromAddr
        message['To'] = settings.toAddr
        message['Cc'] = ', '.join(settings.cc)
        message['Bcc'] = ', '.join(settings.bcc)
        message.attach(part1)
        message.attach(part2)
        text = message.as_string()
        
        try:
            if settings.secure.lower() == 'tls':
                server = smtplib.SMTP(settings.host, settings.port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(settings.host, settings.port)

            server.login(settings.login, settings.password)
            server.sendmail(settings.fromAddr, settings.toAddr, text)
            server.quit()

        except Exception as e:
            message = str(e)
            return StiResult.getError(message)

        return result
    
    def getEventResult(self) -> StiResult:
        if self.request.event == StiEventType.OPENED_REPORT:
            return self.__getOpenedReportResult()
        
        if self.request.event == StiEventType.PRINT_REPORT:
            return self.__getPrintReportResult()

        if self.request.event == StiEventType.BEGIN_EXPORT_REPORT:
            return self.__getBeginExportReportResult()
        
        if self.request.event == StiEventType.END_EXPORT_REPORT:
            return self.__getEndExportReportResult()
        
        """
        if self.request.event == StiEventType.INTERACTION:
            return self.__getInteractionResult()
        """
        
        if self.request.event == StiEventType.EMAIL_REPORT:
            return self.__getEmailReportResult()

        if self.report != None:
            return self.report.getEventResult()
        
        return super().getEventResult()
    

### HTML

    def _getComponentHtml(self) -> str:
        result = super()._getComponentHtml()

        result += self.options.getHtml()
        result += f"let {self.id} = new Stimulsoft.Viewer.StiViewer({self.options.id}, '{self.id}', false);\n"

        result += self.onPrepareVariables.getHtml(True)
        result += self.onBeginProcessData.getHtml(True)
        result += self.onEndProcessData.getHtml()
        result += self.onOpenReport.getHtml()
        result += self.onOpenedReport.getHtml(True)
        result += self.onPrintReport.getHtml(True)
        result += self.onBeginExportReport.getHtml(True)
        result += self.onEndExportReport.getHtml(False, True)
        result += self.onInteraction.getHtml(True, False, False)
        result += self.onEmailReport.getHtml(True)
        result += self.onDesignReport.getHtml(False, False, False)

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
            self.options.toolbar.showFullScreenButton = False
            self.options.appearance.fullScreenMode = True

        return super().getHtml(mode)


### Constructor

    def __init__(self):
        super().__init__()

        self.id = 'viewer'
        self.options = StiViewerOptions()
        self.handler = StiHandler()
