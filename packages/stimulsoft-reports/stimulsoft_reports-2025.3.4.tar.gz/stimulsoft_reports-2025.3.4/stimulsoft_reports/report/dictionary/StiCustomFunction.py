from stimulsoft_data_adapters.classes.StiFunctions import StiFunctions

from ...classes.StiElement import StiElement
from ...enums.Types import Types


class StiCustomFunction(StiElement):
    
### Fields

    __category: str
    __groupFunctionName: str
    __functionName: str
    __description: str
    __typeOfFunction: str
    __returnType: Types
    __returnDescription: str
    __argumentTypes: list
    __argumentNames: list
    __argumentDescriptions: list
    __jsFunction: str


### Methods

    def __getJavaScriptTypes(self, types: list) -> str:
        if isinstance(types, list):
            result = ''
            for type in types:
                if len(result) > 0: result += ', '
                result += StiFunctions.getJavaScriptValue(type)
                
            return f'[{result}]'
        
        return 'null'


    def _equals(self, category: str, groupFunctionName: str, functionName: str, description: str, typeOfFunction: str, returnType: Types, 
                returnDescription: str, argumentTypes: list, argumentNames: list, argumentDescriptions: list, jsFunction: str):
        
        return self.__category == category and self.__groupFunctionName == groupFunctionName and self.__functionName == functionName and \
               self.__description == description and self.__typeOfFunction == typeOfFunction and self.__returnType == returnType and \
               self.__returnDescription == returnDescription and self.__argumentTypes == argumentTypes and self.__argumentNames == argumentNames and \
               self.__argumentDescriptions == argumentDescriptions and self.__jsFunction == jsFunction

### HTML

    def getHtml(self) -> str:
        result = ''

        category = StiFunctions.getJavaScriptValue(self.__category)
        groupFunctionName = StiFunctions.getJavaScriptValue(self.__groupFunctionName)
        functionName = StiFunctions.getJavaScriptValue(self.__functionName)
        description = StiFunctions.getJavaScriptValue(self.__description)
        typeOfFunction = StiFunctions.getJavaScriptValue(self.__typeOfFunction)
        returnType = StiFunctions.getJavaScriptValue(self.__returnType)
        returnDescription = StiFunctions.getJavaScriptValue(self.__returnDescription)
        argumentTypes = self.__getJavaScriptTypes(self.__argumentTypes)
        argumentNames = StiFunctions.getJavaScriptValue(self.__argumentNames)
        argumentDescriptions = StiFunctions.getJavaScriptValue(self.__argumentDescriptions)

        result += \
            f'Stimulsoft.Report.Dictionary.StiFunctions.addFunction({category}, {groupFunctionName}, {functionName}, {description}, {typeOfFunction}, ' \
            f'{returnType}, {returnDescription}, {argumentTypes}, {argumentNames}, {argumentDescriptions}, {self.__jsFunction});\n'

        return result + super().getHtml()


### Constructor

    def __init__(self, category: str, groupFunctionName: str, functionName: str, description: str, typeOfFunction: str, returnType: Types,
                 returnDescription: str, argumentTypes: list, argumentNames: list, argumentDescriptions: list, jsFunction: str):
        
        self.__category = category
        self.__groupFunctionName = groupFunctionName
        self.__functionName = functionName
        self.__description = description
        self.__typeOfFunction = typeOfFunction
        self.__returnType = returnType
        self.__returnDescription = returnDescription
        self.__argumentTypes = argumentTypes
        self.__argumentNames = argumentNames
        self.__argumentDescriptions = argumentDescriptions
        self.__jsFunction = jsFunction
