from stimulsoft_data_adapters.classes.StiBaseResponse import StiBaseResponse
from stimulsoft_data_adapters.enums.StiDataType import StiDataType

from ..classes.StiFileResult import StiFileResult


class StiResponse(StiBaseResponse):
    
### Properties

    @property
    def mimeType(self) -> str:
        """Returns the MIME type for the handler response."""

        if (isinstance(self.result, StiFileResult)):
            dataType: StiDataType = self.result.dataType
            return dataType.value
        
        return super().mimeType
    
    @property
    def data(self) -> bytes:
        """Returns the handler response as a byte array. When using encryption, the response will be encrypted and encoded into a Base64 string."""
        
        if (isinstance(self.result, StiFileResult)):
            return self.result.data
        
        return super().data