from datetime import datetime

from stimulsoft_data_adapters.classes.StiBaseHandler import StiBaseHandler
from stimulsoft_data_adapters.classes.StiFunctions import StiFunctions
from stimulsoft_data_adapters.enums.StiDatabaseType import StiDatabaseType
from stimulsoft_data_adapters.events.StiEvent import StiEvent

from ..classes.StiComponent import StiComponent
from ..enums import StiHtmlMode
from ..enums.StiComponentType import StiComponentType
from ..enums.StiEventType import StiEventType
from .StiFileResult import StiFileResult
from .StiRequest import StiRequest
from .StiResponse import StiResponse
from .StiResult import StiResult


class StiHandler(StiBaseHandler):
    """
    Event handler for all requests from components. Processes the incoming request, communicates with data adapters, 
    prepares parameters and triggers events, and performs all necessary actions. After this, the event handler 
    prepares a response for the web server.
    """

### Fields

    __htmlRendered = False
    __cookie = None
    __component: StiComponent = None


### Properties
    
    @property
    def component(self) -> StiComponent:
        if self.__component != None:
            return self.__component

        if self.request != None:
            if self.request.sender == 'Report':
                from ..report.StiReport import StiReport
                return StiReport()
                
            if self.request.sender == 'Viewer':
                from ..viewer.StiViewer import StiViewer
                return StiViewer()

            if self.request.sender == 'Designer':
                from ..designer.StiDesigner import StiDesigner
                return StiDesigner()
        
        return None
    
    @component.setter
    def component(self, value):
        self.__component = value


    request: StiRequest = None

    timeout = 30
    """Timeout for waiting for a response from the server side, in seconds."""
    
    encryptData = True
    """Enables encryption of data transmitted between the client and the server."""

    escapeQueryParameters = True
    """Enables automatic escaping of parameters in SQL queries."""

    passQueryParametersToReport = False
    """Enables automatic passing of GET parameters from the current URL to the report as variables."""

    allowFileDataAdapters = True
    """
    Allows server-side processing of file data such as XML, JSON, and CSV.
    This improves functionality but may slow down data loading speed a bit.
    """
    

### Events

    @property
    def onPrepareVariables(self) -> StiEvent:
        """The event is invoked before rendering a report after preparing report variables. Python and JavaScript functions are supported."""
        return self._getEvent('onPrepareVariables')

    @onPrepareVariables.setter
    def onPrepareVariables(self, value):
        self._setEvent('onPrepareVariables', value)


### Helpers

    def _createRequest(self):
        return StiRequest()
    
    def _checkEvent(self):
        return self.request.event.value in StiEventType.getValues()
    
    def _checkCommand(self):
        if self.request.event == StiEventType.BEGIN_PROCESS_DATA:
            return super()._checkCommand()
        
        return True
    
    def __getCsrfToken(self) -> str:
        if isinstance(self.__cookie, dict):
            csrf = self.__cookie.get('csrftoken')
            return str(csrf) if csrf != None else None

        return None

    def setCookies(self, cookie):
        """Sets a string with cookies that will be passed when requesting events."""
        
        self.__cookie = cookie

    def getNodejsId(self) -> str:
        return self.component.nodejs.id if self.component != None and self.component.componentType == StiComponentType.REPORT else None

    def getEngineType(self) -> int:
        from ..report.enums.StiEngineType import StiEngineType
        return self.component.engine.value \
            if self.component != None and self.component.componentType == StiComponentType.REPORT \
            else StiEngineType.CLIENT_JS.value


### Results

    def __getPrepareVariablesResult(self) -> StiResult:
        if len(self.onPrepareVariables) > 0:
            from ..events.StiVariablesEventArgs import StiVariablesEventArgs
            from ..report.enums.StiVariableType import StiVariableType
            
            args = StiVariablesEventArgs(self.request)
            result = self.onPrepareVariables.getResult(args)
            if result == None:
                result = StiResult.getSuccess()
                
            result.handlerVersion = self.version
            result.variables = list()

            if not result.success:
                return result

            for variableName in args.variables:
                variable = args.variables[variableName]
                variableChanged = True
                for variableOriginal in self.request.variables:
                    valueOriginal = variableOriginal['value']
                    if variableOriginal['name'] == variableName:
                        if variable.typeName[-5:] == 'Range' and type(variable.value) == dict:
                            value = variable.value
                            variableChanged = value.get('from') != valueOriginal.get('from') or value.get('to') != valueOriginal.get('to')
                        elif variable.typeName[-4:] == 'List' and type(variable.value) == list:
                            value = variable.value
                            variableChanged = len(value) != len(valueOriginal) or len(value) != sum([1 for i, j in zip(value, valueOriginal) if i == j])
                        else:
                            variableChanged = variableOriginal['value'] != variable.value
                        break
                if variableChanged:
                    if variable.type == StiVariableType.DATETIME and type(variable.value) == datetime:
                        variable.value = variable.value.strftime('%Y-%m-%d %H:%M:%S')
                    result.variables.append({ 'name': variable.name, 'type': variable.typeName, 'value': variable.value })
        else:
            result = StiResult.getError("The handler for the 'onPrepareVariables' event is not specified.")

        return result

    def getResponse(self) -> StiResponse:
        """
        Returns the result of processing a request from the client side. The response object will contain the data for the response, 
        as well as their MIME type, Content-Type, and other useful information to create a web server response.
        """

        return StiResponse(self)
    
    def getResult(self):
        """
        Returns the result of processing a request from the client side. The result object will contain a collection of data, 
        message about the result of the command execution, and other technical information.
        """

        if self.request.event == StiEventType.GET_RESOURCE:
            try:
                from stimulsoft_dashboards.resources.StiResourcesHelper import \
                    StiResourcesHelper
            except Exception as e:
                from ..resources.StiResourcesHelper import StiResourcesHelper
            
            result: StiFileResult = StiResourcesHelper.getResult(self.request.data)
            if result.success and self.request.data == 'stimulsoft.handler.js':
                result.data = self.__getJavaScript(result.data).encode()
                result.handlerVersion = self.version

            return result
        
        if self.request.event == StiEventType.PREPARE_VARIABLES:
            return self.__getPrepareVariablesResult()
        
        component = self.component
        if component != None:

            # New component for event
            if self.__component == None:
                component.handler = self
                # TODO: add all events to StiHandler
                #eventName = f"on{self.request.event}"
                #setattr(component, eventName, getattr(self, eventName))

            # Process component event
            result = component.getEventResult()
            if result != None:
                result.handlerVersion = self.version
                return result
        
        return super().getResult()


### JavaScript

    def __getJavaScript(self, data: bytes = None) -> str:
        if data == None:
            from ..resources.StiResourcesHelper import StiResourcesHelper
            result: StiFileResult = StiResourcesHelper.getResult('stimulsoft.handler.js')
            data = result.data
            if not result.success:
                return f'// {result.notice}'

        script = data.decode()
        script = script.replace('{databases}', StiFunctions.getJavaScriptValue(StiDatabaseType.getValues()))
        script = script.replace('{url}', StiFunctions.getJavaScriptValue(self.url))
        script = script.replace('{timeout}', StiFunctions.getJavaScriptValue(self.timeout))
        script = script.replace('{encryptData}', StiFunctions.getJavaScriptValue(self.encryptData))
        script = script.replace('{passQueryParametersToReport}', StiFunctions.getJavaScriptValue(self.passQueryParametersToReport))
        script = script.replace('{checkDataAdaptersVersion}', StiFunctions.getJavaScriptValue(self.checkDataAdaptersVersion))
        script = script.replace('{escapeQueryParameters}', StiFunctions.getJavaScriptValue(self.escapeQueryParameters))
        script = script.replace('{framework}', StiFunctions.getJavaScriptValue('Python'))
        script = script.replace('{cookie}', StiFunctions.getJavaScriptValue(self.__cookie))
        script = script.replace('{csrfToken}', StiFunctions.getJavaScriptValue(self.__getCsrfToken()))
        script = script.replace('{allowFileDataAdapters}', StiFunctions.getJavaScriptValue(self.allowFileDataAdapters))
        script = script.replace('{nodejsId}', StiFunctions.getJavaScriptValue(self.getNodejsId()))
        script = script.replace('{engineType}', StiFunctions.getJavaScriptValue(self.getEngineType()))

        return script
    

### HTML

    def getHtml(self, mode = StiHtmlMode.HTML_SCRIPTS) -> str:
        """
        Gets the HTML representation of the component or element.
        
        mode:
            HTML code generation mode.
        
        return:
            Prepared HTML and JavaScript code for embedding in an HTML template.
        """

        result = ''
        if mode == StiHtmlMode.HTML_SCRIPTS or mode == StiHtmlMode.HTML_PAGE:
            result += '<script type="text/javascript">\n'

        result += self.__getJavaScript() + '\n'

        if mode == StiHtmlMode.HTML_SCRIPTS or mode == StiHtmlMode.HTML_PAGE:
            result += '</script>\n'

        self.__htmlRendered = True

        return result


### Constructor

    def __init__(self, url: str = None, timeout = 30):
        super().__init__(url)
        
        self.timeout = timeout
