from ...classes.StiElement import StiElement
from ...enums.Types import Types
from ..dictionary.StiCustomFunction import StiCustomFunction


class StiFunctions(StiElement):

### Fields

    __functions: list = []


### Methods

    def __exists(category: str, groupFunctionName: str, functionName: str, description: str, typeOfFunction: str, returnType: Types,
                 returnDescription: str = '', argumentTypes: list = None, argumentNames: list = None, argumentDescriptions: list = None,
                 jsFunction: str = None) -> bool:
        func: StiCustomFunction
        for func in StiFunctions.__functions:
            if func._equals(category, groupFunctionName, functionName, description, typeOfFunction, returnType, 
                            returnDescription, argumentTypes, argumentNames, argumentDescriptions, jsFunction):
                return True
            
        return False

    def addFunction(category: str, groupFunctionName: str, functionName: str, description: str, typeOfFunction: str, returnType: Types,
                    returnDescription: str = '', argumentTypes: list = None, argumentNames: list = None, argumentDescriptions: list = None,
                    jsFunction: str = None):
        """
        Adds the specified JavaScript function to the collection for use in the report generator.

        category:
            The name of the category in the designer's data dictionary.

        groupFunctionName:
            The name of a function group in the designer's data dictionary.

        functionName:
            The name of the function.

        description:
            The description of the function.

        typeOfFunction:
            The kind of this function.

        returnType:
            [enum] The return type of the function.
        
        returnDescription:
            The description of the function's return result.

        argumentTypes:
            [enum] The array of function parameter types.

        argumentNames:
            The array of function parameter names.

        argumentDescriptions:
            The array of function parameter descriptions.

        jsFunction:
            The name of an existing JavaScript function, or the JavaScript function itself.
        """
        
        if not StiFunctions.__exists(category, groupFunctionName, functionName, description, typeOfFunction, returnType,
                                     returnDescription, argumentTypes, argumentNames, argumentDescriptions, jsFunction):
            func = StiCustomFunction(
                category, groupFunctionName, functionName, description, typeOfFunction, returnType,
                returnDescription, argumentTypes, argumentNames, argumentDescriptions, jsFunction)
            
            StiFunctions.__functions.append(func)


### HTML

    def getHtml(self) -> str:
        result = ''

        func: StiCustomFunction
        for func in StiFunctions.__functions:
            result += func.getHtml()

        return result + super().getHtml()
