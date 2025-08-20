import re
from enum import Enum, Flag

from ..classes.StiElement import StiElement
from .StiComponent import StiComponent


class StiComponentOptions(StiElement):
    
### Fields

    __component: StiComponent = None


### Properties

    @property
    def id(self) -> str:
        return self.component.id + 'Options' if self.component != None else ''
    
    @property
    def component(self) -> StiComponent:
        return self.__component
    
    @component.setter
    def component(self, value):
        if value != None:
            self.__component = value
            options: dict[str, StiComponentOptions] = {key: getattr(self, key) for key in dir(self) if issubclass(type(getattr(self, key)), StiComponentOptions)}
            for item in options.values():
                item.component = value


### Helpers

    def __getColorValue(self, value: str) -> str:
        if len(value or '') == 0:
            return 'Stimulsoft.System.Drawing.Color.transparent'

        if value[0] == '#':
            value = value.lstrip('#')
            if len(value) == 3:
                value = ''.join([d + d for d in value])
            rgb = tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
            return f'Stimulsoft.System.Drawing.Color.fromArgb(255, {rgb[0]}, {rgb[1]}, {rgb[2]})'

        return f'Stimulsoft.System.Drawing.Color.{value}'
    
    def __getJavaScriptValue(self, prop: str, value: str) -> str:
        if prop[-5:] == 'Color':
            return self.__getColorValue(value)
        
        if value == None:
            return 'null'

        if type(value) == bool:
            return str(value).lower()

        if type(value) == str:
            return f'"{value}"'
        
        if isinstance(value, Enum) or isinstance(value, Flag):
            return value.value
        
        return str(value)
    
    def getLocalizationPath(self, localization: str) -> str:
        if (len(localization or '') == 0):
            return None

        localization = localization.lower()
        if len(localization) < 5 or localization[-4:] != '.xml':
            localization += '.xml'

        if re.search('/[\/\\\]/', localization) == None:
            localization = f"{self.component.handler.url}?sti_event=GetResource&sti_data={localization}"

        return localization


### HTML
    
    def getHtml(self) -> str:
        result = ''
        options = {key: getattr(self, key) for key in dir(self) if not callable(getattr(self, key)) and not key.startswith('_') and type(getattr(type(self), key)) != property}
        for key in options:
            value = getattr(self, key)
            if hasattr(type(self), key) and getattr(type(self), key) != value:
                if issubclass(type(value), StiComponentOptions):
                    suboptions: StiComponentOptions = value
                    result += suboptions.getHtml()
                else:
                    jsValue = self.__getJavaScriptValue(key, value)
                    result += f'{self.id}.{key} = {jsValue};\n'

        return result + super().getHtml()
