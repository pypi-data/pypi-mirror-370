import re

from stimulsoft_data_adapters.classes.StiFunctions import StiFunctions

from ..classes.StiElement import StiElement
from ..enums import FontStyle
from .StiCustomFont import StiCustomFont


class StiFontCollection(StiElement):

### Fields

    __fontsCollection: list = []
    __fontsFolder: str = None


### Methods

    def __exists(filePath: str, fontName: str, fontStyle: FontStyle) -> bool:
        font: StiCustomFont
        for font in StiFontCollection.__fontsCollection:
            if font._equals(filePath, fontName, fontStyle):
                return True
            
        return False


    def addFontFile(filePath: str, fontName: str = None, fontStyle: FontStyle = FontStyle.NONE):
        """
        Adds the specified font file to the collection for use in the report generator.

        filePath:
            Path or URL to the font file.

        fontName:
            Uses the specified name for this font.

        fontStyle:
            [enum] Uses the specified style for this font.
        """
        
        if not StiFunctions.isNullOrEmpty(filePath) and not StiFontCollection.__exists(filePath, fontName, fontStyle):
            filePath = re.sub('/\\\\/', '/', filePath)
            font = StiCustomFont(filePath, fontName, fontStyle)
            StiFontCollection.__fontsCollection.append(font)

    def setFontsFolder(folderPath: str):
        StiFontCollection.__fontsFolder = folderPath
    

### HTML

    def getHtml(self) -> str:
        result = ''

        if not StiFunctions.isNullOrEmpty(StiFontCollection.__fontsFolder):
            folderPath = StiFunctions.getJavaScriptValue(StiFontCollection.__fontsFolder)
            result += f'Stimulsoft.Base.StiFontCollection.setFontsFolder({folderPath});\n'

        font: StiCustomFont
        for font in StiFontCollection.__fontsCollection:
            result += font.getHtml()

        return result + super().getHtml()

    