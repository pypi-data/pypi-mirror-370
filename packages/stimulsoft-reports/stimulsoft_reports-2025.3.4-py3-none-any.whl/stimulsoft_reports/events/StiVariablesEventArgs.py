from datetime import datetime

from stimulsoft_data_adapters.events.StiEventArgs import StiEventArgs

from ..report.dictionary.StiVariable import StiVariable
from ..report.enums.StiVariableType import StiVariableType


class StiVariablesEventArgs(StiEventArgs):

### Fields

    __variables: dict[str, StiVariable] = None


### Properties

    @property
    def variables(self) -> dict[str, StiVariable]:
        """A set of Request from User variables (if they are present in the current report)."""

        return self.__variables
    
    @variables.setter
    def variables(self, value: dict[str, StiVariable] | list):
        if type(value) == dict:
            self.__variables = value
        elif type(value) == list:
            self.__variables = dict()
            from ..report.dictionary.StiVariable import StiVariable
            for item in value:
                variableName = item['name']
                variableValue = item['value']
                variableType = StiVariableType(item['type'])
                if variableType == StiVariableType.DATETIME:
                    variableValue = datetime.strptime(variableValue, '%Y-%m-%d %H:%M:%S')
                elif variableType.value[-5:] == 'Range':
                    variableValue = { 'from': variableValue['from'], 'to': variableValue['to'] }
                elif variableType.value[-4:] == 'List' and type(variableValue) == list:
                    variableValue = variableValue.copy()
                variable = StiVariable(variableName, variableType, variableValue)
                self.__variables[variable.name] = variable
    
