from stimulsoft_data_adapters.classes.StiFunctions import StiFunctions

from ..classes.StiElement import StiElement
from ..enums import FontStyle


class StiCustomFont(StiElement):

### Fields

    __filePath: str
    __fontName: str
    __fontStyle: FontStyle


### Methods

    def _equals(self, filePath: str, fontName: str, fontStyle: FontStyle):
        return self.__filePath == filePath and self.__fontName == fontName and self.__fontStyle == fontStyle


### HTML

    def getHtml(self) -> str:
        result = ''

        filePath = StiFunctions.getJavaScriptValue(self.__filePath)
        fontName = StiFunctions.getJavaScriptValue(self.__fontName)
        fontStyle = StiFunctions.getJavaScriptValue(self.__fontStyle)

        result += f'Stimulsoft.Base.StiFontCollection.addFontFile({filePath}, {fontName}, {fontStyle});\n'

        return result + super().getHtml()
    

### Constructor

    def __init__(self, filePath: str, fontName: str = None, fontStyle: FontStyle = FontStyle.NONE):
        self.__filePath = filePath
        self.__fontName = fontName
        self.__fontStyle = fontStyle