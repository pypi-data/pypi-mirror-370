from enum import Enum


class Encoding(Enum):
    
    ASCII = 'Stimulsoft.System.Text.Encoding.ASCII'
    BIG_ENDIAN_UNICODE = 'Stimulsoft.System.Text.Encoding.BigEndianUnicode'
    DEFAULT = 'Stimulsoft.System.Text.Encoding.Default'
    UNICODE = 'Stimulsoft.System.Text.Encoding.Unicode'
    UTF32 = 'Stimulsoft.System.Text.Encoding.UTF32'
    UTF7 = 'Stimulsoft.System.Text.Encoding.UTF7'
    UTF8 = 'Stimulsoft.System.Text.Encoding.UTF8'
    WINDOWS_1250 = 'Stimulsoft.System.Text.Encoding.Windows1250'
    WINDOWS_1251 = 'Stimulsoft.System.Text.Encoding.Windows1251'
    WINDOWS_1252 = 'Stimulsoft.System.Text.Encoding.Windows1252'
    WINDOWS_1256 = 'Stimulsoft.System.Text.Encoding.Windows1256'
    ISO_8859_1 = 'Stimulsoft.System.Text.Encoding.ISO_8859_1'


### Helpers

    def getByName(encodingName: str):
        name = encodingName.upper().replace('-', '_').replace('BIGENDIANUNICODE', 'BIG_ENDIAN_UNICODE')
        if hasattr(Encoding, name):
            value: Encoding = getattr(Encoding, name)
            return value.value

        return None