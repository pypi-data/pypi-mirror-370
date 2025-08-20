from __future__ import annotations

import typing

from stimulsoft_data_adapters.enums.StiDataType import StiDataType

from ..base.StiFontCollection import StiFontCollection
from ..base.StiLicense import StiLicense
from ..classes.StiElement import StiElement
from ..classes.StiFileResult import StiFileResult
from ..classes.StiJavaScript import StiJavaScript
from ..classes.StiRequest import StiRequest
from ..classes.StiResponse import StiResponse
from ..classes.StiResult import StiResult
from ..enums.StiComponentType import StiComponentType
from ..enums.StiHtmlMode import StiHtmlMode

if typing.TYPE_CHECKING:
    from ..events.StiComponentEvent import StiComponentEvent
    from ..report.dictionary.StiFunctions import StiFunctions
    from ..report.StiReport import StiReport
    from .StiHandler import StiHandler
    

class StiComponent(StiElement):

### Events

    @property
    def onDatabaseConnect(self) -> StiComponentEvent:
        """The event is invoked before connecting to the database after all parameters have been received. Only Python functions are supported."""
        return self._getEvent('onDatabaseConnect')

    @onDatabaseConnect.setter
    def onDatabaseConnect(self, value):
        self._setEvent('onDatabaseConnect', value)


    @property
    def onPrepareVariables(self) -> StiComponentEvent:
        """The event is invoked before rendering a report after preparing report variables. Python and JavaScript functions are supported."""
        return self._getEvent('onPrepareVariables')

    @onPrepareVariables.setter
    def onPrepareVariables(self, value):
        self._setEvent('onPrepareVariables', value)


    @property
    def onBeginProcessData(self) -> StiComponentEvent:
        """The event is invoked before data request, which needed to render a report. Python and JavaScript functions are supported."""
        return self._getEvent('onBeginProcessData')

    @onBeginProcessData.setter
    def onBeginProcessData(self, value):
        self._setEvent('onBeginProcessData', value)


    @property
    def onEndProcessData(self) -> StiComponentEvent:
        """The event is invoked after loading data before rendering a report. Python and JavaScript functions are supported."""
        return self._getEvent('onEndProcessData')

    @onEndProcessData.setter
    def onEndProcessData(self, value):
        self._setEvent('onEndProcessData', value)


### Fields
    
    __events: dict = None
    __handler: StiHandler = None
    __processRequestResult: bool = None
    __javascript: StiJavaScript = None
    __license: StiLicense = None
    __fontCollection: StiFontCollection = None
    __functions: StiFunctions = None


### Properties

    @property
    def componentType(self) -> StiComponentType:
        return None


    @property
    def handler(self) -> StiHandler:
        """
        Gets or sets an event handler that controls data passed from client to server and from server to client.
        Contains the necessary options for sending data.
        """
        
        return self.__handler
    
    @handler.setter
    def handler(self, value: StiHandler):
        if value != None:
            value._setEvents(self.__events)
            
            # The component must be original, since it usually processes requests
            if value.component == None:
                value.component = self
            
            self.__handler = value


    @property
    def request(self) -> StiRequest:
        return self.handler.request if self.handler != None else None


    @property
    def javascript(self) -> StiJavaScript:
        """Gets a JavaScript manager that controls the deployment of JavaScript code necessary for components to work."""

        return self.__javascript
    

    @property
    def license(self) -> StiLicense:
        """Gets a license manager that allows you to load a license key in various formats."""

        return self.__license
    
    @license.setter
    def license(self, value: StiLicense):
        self.__license = value


    @property
    def fontCollection(self) -> StiFontCollection:
        return self.__fontCollection
    
    @fontCollection.setter
    def fontCollection(self, value: StiFontCollection):
        if value != None and isinstance(value, StiFontCollection):
            self.__fontCollection = value
    

    @property
    def functions(self) -> StiFunctions:
        return self.__functions
    
    @functions.setter
    def functions(self, value: StiFunctions):
        from ..report.dictionary.StiFunctions import StiFunctions
        if value != None and isinstance(value, StiFunctions):
            self.__functions = value


### Events

    def _getEvent(self, name) -> StiComponentEvent:
        event = self.__events.get(name)
        if event == None:
            from ..events.StiComponentEvent import StiComponentEvent
            event = StiComponentEvent(self, name)
            self.__events[name] = event

        return event
    
    def _setEvent(self, name, value):
        from ..events.StiComponentEvent import StiComponentEvent
        if isinstance(value, StiComponentEvent):
            self.__events[name] = value
        elif callable(value) or isinstance(value, (bool, str)):
            self._getEvent(name).append(value)

    def _setEventsFrom(self, component: StiComponent):
        # Copying events unique to self object, if they have been set
        for event in self.__events:
            if not event in component.__events:
                component.__events[event] = self.__events.get(event)

        self.__events = component.__events
    
    def getEventResult(self) -> StiResult:
        return None


### Request

    def processRequest(self, request: object = None, query: dict | str = None, body: bytes | str = None) -> bool:
        """
        Processing an HTTP request from the client side of the component. If successful, it is necessary to return a response 
        with the processing result, which can be obtained using the 'getResponse()' or 'getFrameworkResponse()' functions.
        
        request
            A request object for one of the supported frameworks.

        query:
            The GET query string if no framework request is specified.
        
        body:
            The POST form data if no framework request is specified.

        return:
            True if the request was processed successfully.
        """

        self.__processRequestResult = self.handler.processRequest(request, query, body)
        return self.__processRequestResult
    
    def getResponse(self) -> StiResponse:
        """
        Returns the result of processing a request from the client side. The response object will contain the data for the response, 
        as well as their MIME type, Content-Type, and other useful information to create a web server response.
        """

        if self.__processRequestResult == False:
            html = self.getHtml(StiHtmlMode.HTML_PAGE)
            result = StiFileResult(html, StiDataType.HTML)
            return StiResponse(self.handler, result)

        self.__processRequestResult = None
        return self.handler.getResponse()
    
    def getFrameworkResponse(self, handler = None) -> object:
        """Returns the result of processing a request from the client side intended for one of the supported frameworks."""
        
        return self.getResponse().getFrameworkResponse(handler)


### HTML

    def _setHtmlRendered(self, value):
        self.htmlRendered = value
        self.license.htmlRendered = value
        self.fontCollection.htmlRendered = value
        self.functions.htmlRendered = value

    def _getComponentHtml(self) -> str:
        result = ''

        if not self.license.htmlRendered:
            result += self.license.getHtml()

        if not self.__fontCollection.htmlRendered:
            result += self.__fontCollection.getHtml()

        if not self.__functions.htmlRendered:
            result += self.__functions.getHtml()

        return result
    
    def _getBeforeRenderCallback(self, renderHtml: str) -> str:
        """
        Wrapper for registering server-side data in the report.
        
        renderHtml:
            The code for building (StiReport) or assigning (StiViewer, StiDesigner) the report.
        """

        from ..report.StiReport import StiReport
        reportId = self.id if isinstance(self, StiReport) else self.report.id
        result = f'{reportId}BeforeRenderCallback = function (args) {{\n'
        result += 'if (args.data && args.data.data) {\n'
        result += f'{reportId}.regData(args.data.name, args.data.name, args.data.data);\n'
        result += f'if (args.data.synchronize) {reportId}.dictionary.synchronize();\n'
        result += '}\n'
        result += f"{renderHtml}}}\n"

        return result

    def getHtml(self, mode = StiHtmlMode.HTML_SCRIPTS) -> str:
        """
        Gets the HTML representation of the component.
        
        mode:
            HTML code generation mode.
        
        return:
            Prepared HTML and JavaScript code for embedding in an HTML template.
        """

        result = ''

        if mode == StiHtmlMode.HTML_PAGE:
            result += '<!DOCTYPE html>\n<html>\n<head>\n'
            result += self.javascript.getHtml()
            result += '</head>\n<body onload="start()">\n'

        if mode == StiHtmlMode.HTML_SCRIPTS or mode == StiHtmlMode.HTML_PAGE:
            if self.componentType == StiComponentType.VIEWER or self.componentType == StiComponentType.DESIGNER:
                result += f'<div id="{self.id}Content"></div>\n'

            result += '<script type="text/javascript">\n'

        if mode == StiHtmlMode.HTML_PAGE:
            result += 'function start() {\n'

        result += self._getComponentHtml()

        if mode == StiHtmlMode.HTML_PAGE:
            result += '}\n'

        if mode == StiHtmlMode.HTML_SCRIPTS or mode == StiHtmlMode.HTML_PAGE:
            result += '</script>\n'

        if mode == StiHtmlMode.HTML_PAGE:
            result += '</body>\n</html>'

        return result + super().getHtml()
    
    
### Constructor

    def __init__(self):
        self.__events = dict()
        self.__javascript = StiJavaScript(self)
        self.__license = StiLicense()
        self.__fontCollection = StiFontCollection()
        from ..report.dictionary.StiFunctions import StiFunctions
        self.__functions = StiFunctions()
        self.onBeginProcessData += True