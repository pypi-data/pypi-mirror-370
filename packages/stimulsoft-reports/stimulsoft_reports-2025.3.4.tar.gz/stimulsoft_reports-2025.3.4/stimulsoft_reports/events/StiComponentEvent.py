from stimulsoft_data_adapters.classes.StiFunctions import StiFunctions
from stimulsoft_data_adapters.events.StiEvent import StiEvent
from stimulsoft_data_adapters.events.StiEventArgs import StiEventArgs

from ..classes.StiComponent import StiComponent
from ..classes.StiResult import StiResult
from ..enums.StiComponentType import StiComponentType


class StiComponentEvent(StiEvent):
    
### Fields

    __component: StiComponent = None
    __htmlRendered: bool = False


### Properties

    @property
    def handler(self):
        return self.component.handler if self.component.handler != None else super().handler
    
    @property
    def component(self):
        return self.__component
    
    @property
    def htmlRendered(self) -> str:
        return self.__htmlRendered

    
### Helpers

    def getResult(self, args: StiEventArgs, resultClass = None) -> StiResult:
        if resultClass == None:
            resultClass = StiResult

        return super().getResult(args, resultClass)

    def _setArgs(self, *args, **keywargs) -> StiEventArgs:
        eventArgs = super()._setArgs(*args, **keywargs)
        if isinstance(eventArgs, StiEventArgs):
            eventArgs.sender = self.component

        return eventArgs


### HTML

    def getHtml(self, callback = False, prevent = False, process = True, internal = False) -> str:
        """
        Gets the HTML representation of the event.

        callback:
            Adding a callback function.

        prevent:
            Preventing standard client-side processing.

        process:
            Processing event on the server side.

        internal:
            A custom event that is not supported by the JavaScript component.
        """

        if (len(self) == 0 or self.__htmlRendered):
            return ''
        
        result = ''
        componentId = self.component.id
        clientScript = ''
        eventName = self.name[2:]
        callback = callback and self.hasServerCallbacks()
        process = process and self.hasServerCallbacks()

        # Prepare client-side events
        for callbackName in self.callbacks:
            if type(callbackName) == str:
                clientScript += \
                    f'if (typeof {callbackName} === "function") {callbackName}(args); ' \
                    if StiFunctions.isJavaScriptFunctionName(callbackName) else \
                    f'{callbackName} '

        # Prepare args for internal event
        if internal:
            componentType = self.component.componentType.value
            reportId = componentId if self.component.componentType == StiComponentType.REPORT else \
                (f"{componentId}.{self.component.report.id}" if self.component.report != None else "null")

            result += f'var args = {{event: "{eventName}", sender: "{componentType}", report: {reportId}, preventDefault: false}};\n'
            if not StiFunctions.isNullOrEmpty(clientScript):
                result += f'{clientScript}\n'

        # For an internal event, the args and the callback function must have a unique name
        callbackName = self.component.id + eventName + 'Callback' if internal else 'callback'
        argsArgument = f'args{eventName}' if internal else 'args'

        # Prepare event parameters
        callbackArgument = f', {callbackName}' if callback else ''
        preventValue = 'args.preventDefault = true; ' if prevent else ''
        processValue = f'Stimulsoft.handler.process({argsArgument}{callbackArgument}); ' if process else (f'{callbackName}(); ' if callback else '')

        # For an internal event, the function is called in the next JavaScript frame (a zero timeout is used)
        internalValue = f'let {argsArgument} = args;\nlet {callbackName} = null;\nsetTimeout(function () {{ {preventValue}{processValue}}});\n' if callback else ''
        eventValue = f'{componentId}.{self.name} = function (args{callbackArgument}) {{ {preventValue}{clientScript}{processValue}}};\n'
        result += internalValue if internal else eventValue

        self.__htmlRendered = True
        return result
    

### Constructor

    def __init__(self, component: StiComponent, name: str):
        super().__init__(component.handler, name)
        self.__component = component