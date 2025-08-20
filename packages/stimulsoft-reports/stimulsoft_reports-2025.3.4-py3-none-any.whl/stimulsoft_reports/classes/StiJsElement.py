from enum import Enum, Flag

from .StiElement import StiElement


class StiJsElement(StiElement):

### Helpers

    def _getIgnoredProperties(self) -> list:
        return ['id', 'htmlRendered']
    
    def _getStringValue(self, name: str, value) -> str:
        if value == None:
            return 'null'

        if type(value) == bool:
            return str(value).lower()
        
        if type(value) == str:
            return f'"{value}"'
        
        if isinstance(value, Enum) or isinstance(value, Flag):
            return value.value
        
        return str(value)

    def _getProperties(self) -> list:
        ignored = self._getIgnoredProperties()
        return [name for name in dir(self) if not name.startswith('_') and not callable(getattr(self, name)) and not name in ignored]
    
    def _setProperty(self, name, value):
        selfvalue = getattr(self, name)
        if isinstance(selfvalue, StiJsElement): selfvalue.setObject(value)
        elif isinstance(selfvalue, Enum) or isinstance(value, Flag): setattr(self, name, selfvalue.__class__(value))
        else: setattr(self, name, value)

    def getObject(self) -> dict:
        properties = self._getProperties()
        result = dict()
        for name in properties:
            value = getattr(self, name)
            if isinstance(value, StiJsElement): result[name] = value.getObject()
            elif isinstance(value, Enum) or isinstance(value, Flag): result[name] = value.value
            else: result[name] = value
        
        return result
    
    def setObject(self, object: dict):
        properties = self._getProperties()
        for name in properties:
            if name in object:
                value = object.get(name)
                self._setProperty(name, value)