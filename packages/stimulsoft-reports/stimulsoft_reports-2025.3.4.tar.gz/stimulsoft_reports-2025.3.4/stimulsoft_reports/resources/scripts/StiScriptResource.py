from importlib import resources

from stimulsoft_data_adapters.enums.StiDataType import StiDataType

from ...classes.StiFileResult import StiFileResult


class StiScriptResource:

    def getResult(name: str) -> StiFileResult:
        try:
            data = resources.read_binary(__package__, name)
        except Exception as e:
            message = str(e)
            return StiFileResult.getError(message)
        
        return StiFileResult(data, StiDataType.JAVASCRIPT)