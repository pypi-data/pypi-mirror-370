from ...classes.StiElement import StiElement
from ..enums.StiVariableType import StiVariableType


class StiVariable(StiElement):
    
### Properties

    name: str = None
    """Gets or sets the name of the variable."""

    type: StiVariableType = None
    """Gets or sets the type of the variable."""

    value = None
    """Gets or sets the value of the variable. The type of object depends on the type of variable."""

    @property
    def typeName(self) -> str:
        """Gets the string name of the variable type."""

        return self.type.value if self.type != None else None


### HTML

    def getHtml(self) -> str:
        result = \
            f"let {self.id} = new Stimulsoft.Report.Dictionary.StiVariable" \
            f"('', '{self.name}', '{self.name}', '', Stimulsoft.System.{self.type.value}, '{self.value}');\n"
        
        return result + super().getHtml()


### Constructor

    def __init__(self, name: str, type = StiVariableType.STRING, value: object = ''):
        """
        name:
            The name of the variable.

        type:
            The type of the variable.
        
        value:
            The value of the variable. The type of value object depends on the type of variable.
        """

        self.id = "variable" + name
        self.name = name
        self.type = type
        self.value = value