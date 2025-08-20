from ..classes.StiElement import StiElement
from .StiLicenseStatic import StiLicenseStatic


class StiLicense(StiElement):

### Fields

    __licenseKey: str = None
    __licenseFile: str = None


### Helpers

    def __clearKey(self) -> None:
        self.__licenseKey = None
        self.__licenseFile = None

    def __getStaticKey(self) -> str:
        for field in dir(StiLicenseStatic):
            if field.endswith('__licenseKey'):
                return getattr(StiLicenseStatic, field)
            
    def __getStaticFile(self) -> str:
        for field in dir(StiLicenseStatic):
            if field.endswith('__licenseFile'):
                return getattr(StiLicenseStatic, field)
    

### License

    def setKey(self, key: str) -> None:
        """Sets the license key in Base64 format."""
    
        self.__clearKey()
        self.__licenseKey = key

    def setFile(self, file: str) -> None:
        """Sets the path or URL to the license key file."""
    
        self.__clearKey()
        self.__licenseFile = file


### HTML

    def getHtml(self) -> str:
        result = ''

        if len(self.__licenseKey or '') == 0:
            self.__licenseKey = self.__getStaticKey()
        
        if len(self.__licenseFile or '') == 0:
            self.__licenseFile = self.__getStaticFile()
        
        if len(self.__licenseKey or '') > 0:
            result = f"Stimulsoft.Base.StiLicense.Key = '{self.__licenseKey}';\n"
            
        elif len(self.__licenseFile or '') > 0:
            result = f"Stimulsoft.Base.StiLicense.loadFromFile('{self.__licenseFile}');\n"

        return result + super().getHtml()
        