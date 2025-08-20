from enum import Enum


class Types(Enum):
    
    INT = 'Stimulsoft.System.Int32'
    LONG = 'Stimulsoft.System.Int64'
    STRING = 'String'
    BOOL = 'Boolean'
    BYTE = 'Stimulsoft.System.Byte'
    SHORT = 'Stimulsoft.System.Int16'
    CHAR = 'Stimulsoft.System.Char'
    DOUBLE = 'Stimulsoft.System.Double'
    FLOAT = 'Stimulsoft.System.Single'
    DECIMAL = 'Stimulsoft.System.Decimal'
    OBJECT = 'Object'
    DATETIME = 'Stimulsoft.System.DateTime'
    TIMESPAN = 'Stimulsoft.System.TimeSpan'