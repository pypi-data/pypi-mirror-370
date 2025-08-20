from .enums.StiExportFormat import StiExportFormat
from .enums.StiImageFormat import StiImageFormat
from .enums.StiImageResolutionMode import StiImageResolutionMode
from .enums.StiMonochromeDitheringType import StiMonochromeDitheringType
from .enums.StiPdfAllowEditable import StiPdfAllowEditable
from .enums.StiPdfAutoPrintMode import StiPdfAutoPrintMode
from .enums.StiPdfComplianceMode import StiPdfComplianceMode
from .enums.StiPdfEncryptionKeyLength import StiPdfEncryptionKeyLength
from .enums.StiPdfImageCompressionMethod import StiPdfImageCompressionMethod
from .enums.StiPdfZUGFeRDComplianceMode import StiPdfZUGFeRDComplianceMode
from .enums.StiUserAccessPrivileges import StiUserAccessPrivileges
from .StiExportSettings import StiExportSettings


class StiPdfExportSettings(StiExportSettings):
    """Class describes settings for export to Adobe PDF format."""

### Properties

    imageQuality = 0.75
    """Gets or sets image quality of images which will be exported to result file."""

    imageResolution = 100
    """Gets or sets image resolution of images which will be exported to result file."""

    imageResolutionMode = StiImageResolutionMode.AUTO
    """[enum] Gets or sets image resolution mode."""

    embeddedFonts = True
    """Gets or sets value which indicates that fonts which used in report will be included in PDF file."""

    standardPdfFonts = False
    """Gets or sets value which indicates that only standard PDF fonts will be used in result PDF file."""

    compressed = True
    """Gets or sets value which indicates that result file will be used compression."""

    useUnicode = True
    """Gets or sets value which indicates that unicode symbols must be used in result PDF file."""

    useDigitalSignature = False
    """Gets or sets value which indicates that digital signature is used for creating PDF file."""

    getCertificateFromCryptoUI = True
    """Gets or sets value which indicates that certificate for PDF file digital signing must be get with help of special GUI."""

    exportRtfTextAsImage = False
    """Gets or sets value which indicates that rtf text will be exported as bitmap images or as vector images."""

    passwordInputUser = ''
    """Gets or sets user password for created PDF file."""

    passwordInputOwner = ''
    """Gets or sets owner password for created PDF file."""

    userAccessPrivileges = StiUserAccessPrivileges.ALL
    """[enum] Gets or sets user access privileges when Adobe PDF file is viewing."""

    keyLength = StiPdfEncryptionKeyLength.BIT40
    """[enum] Gets or sets length of encryption key."""

    creatorString = ''
    """Gets or sets information about the creator to be inserted into result PDF file."""

    keywordsString = ''
    """Gets or sets keywords information to be inserted into result PDF file."""

    imageCompressionMethod = StiPdfImageCompressionMethod.JPEG
    """[enum] Gets or sets mode of image compression in PDF file."""

    imageIndexedColorPaletteSize = 96
    """Gets or sets a Palette size for the Indexed color mode of image compression."""

    imageFormat = StiImageFormat.COLOR
    """[enum] Gets or sets image format for exported images."""

    ditheringType = StiMonochromeDitheringType.FLOYD_STEINBERG
    """[enum] Gets or sets type of dithering."""

    @property
    def pdfACompliance(self) -> bool:
        """Gets or sets value which indicates that resulting PDF file is PDF/A compliance."""

        return self.pdfComplianceMode != StiPdfComplianceMode.NONE
    
    @pdfACompliance.setter
    def pdfACompliance(self, value: bool):
        self.pdfComplianceMode = StiPdfComplianceMode.A1 if value else StiPdfComplianceMode.NONE

    pdfComplianceMode = StiPdfComplianceMode.NONE
    """[enum] Gets or sets value which indicates the PDF file compliance mode."""

    autoPrintMode = StiPdfAutoPrintMode.NONE
    """[enum] Gets or sets a value indicating AutoPrint mode."""

    allowEditable = StiPdfAllowEditable.NO
    """[enum]"""

    #embeddedFiles: list[StiPdfEmbeddedFileData] = list()

    ZUGFeRDComplianceMode = StiPdfZUGFeRDComplianceMode.NONE
    """[enum] Gets or sets value which indicates the ZUGFeRD compliance mode."""

    ZUGFeRDConformanceLevel = 'BASIC'
    """Gets or sets value which indicates the ZUGFeRD Conformance Level."""

    ZUGFeRDInvoiceData: list = None
    """Gets or sets value of the ZUGFeRD Invoice data."""


### Helpers

    def getExportFormat(self):
        return StiExportFormat.PDF