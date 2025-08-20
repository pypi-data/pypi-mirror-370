from .enums.StiExportFormat import StiExportFormat
from .enums.StiImageFormat import StiImageFormat
from .enums.StiImageType import StiImageType
from .enums.StiMonochromeDitheringType import StiMonochromeDitheringType
from .enums.StiTiffCompressionScheme import StiTiffCompressionScheme
from .StiExportSettings import StiExportSettings


class StiImageExportSettings(StiExportSettings):
    """Class describes settings for export to image formats."""

### Properties

    imageType: StiImageType = None
    """[enum] Gets or sets image type for exported images."""

    imageZoom = 1.0
    """Gets or sets image zoom factor for exported images. This property can't be used with EMF, SVG, SVGZ formats."""

    imageResolution = 100
    """Gets or sets image resolution for exported images. This property can't be used with EMF, SVG, SVGZ formats."""

    cutEdges = False
    """Gets or sets value which indicates that page margins will be cut or not. This property can't be used with EMF, SVG, SVGZ formats."""

    imageFormat = StiImageFormat.COLOR
    """[enum] Gets or sets image format for exported images. This property can't be used with EMF, SVG, SVGZ formats."""

    multipleFiles = False
    """Gets or sets value which indicates that export engine will be create one solid file or multiple files (one file per page).
    This property can't be used with EMF, SVG, SVGZ formats."""

    ditheringType = StiMonochromeDitheringType.FLOYD_STEINBERG
    """[enum] Gets or sets type of dithering. This property can't be used with EMF, SVG, SVGZ formats."""

    tiffCompressionScheme = StiTiffCompressionScheme.DEFAULT
    """[enum] Gets or sets compression scheme of TIFF format. This property can't be used with EMF, SVG, SVGZ formats."""

    compressToArchive = False
    """Gets or sets a value indicating whether it is necessary to save output files as zip-file."""


### Helpers

    def getExportFormat(self):
        if self.imageType == StiImageType.BMP:
            return StiExportFormat.IMAGE_BMP
        
        if self.imageType == StiImageType.GIF:
            return StiExportFormat.IMAGE_GIF
        
        if self.imageType == StiImageType.JPEG:
            return StiExportFormat.IMAGE_JPEG
        
        if self.imageType == StiImageType.PCX:
            return StiExportFormat.IMAGE_PCX
        
        if self.imageType == StiImageType.PNG:
            return StiExportFormat.IMAGE_PNG
        
        if self.imageType == StiImageType.SVG:
            return StiExportFormat.IMAGE_SVG
        
        if self.imageType == StiImageType.SVGZ:
            return StiExportFormat.IMAGE_SVGZ
        
        return StiExportFormat.IMAGE_TIFF
    
    def setImageType(self, format = None):
        if format == None:
            format = self.getExportFormat()
            
        if format == StiExportFormat.IMAGE_BMP:
            self.imageType = StiImageType.BMP

        elif format == StiExportFormat.IMAGE_GIF:
            self.imageType = StiImageType.GIF

        elif format == StiExportFormat.IMAGE_JPEG:
            self.imageType = StiImageType.JPEG

        elif format == StiExportFormat.IMAGE_PCX:
            self.imageType = StiImageType.PCX

        elif format == StiExportFormat.IMAGE_PNG:
            self.imageType = StiImageType.PNG

        elif format == StiExportFormat.IMAGE_SVG:
            self.imageType = StiImageType.SVG

        elif format == StiExportFormat.IMAGE_SVGZ:
            self.imageType = StiImageType.SVGZ
            
        elif format == StiExportFormat.IMAGE_TIFF:
            self.imageType = StiImageType.TIFF


### HTML

    def getHtml(self) -> str:
        self.setImageType()

        return super().getHtml()
    

### Constructor

    def __init__(self, imageType: StiImageType = None):
        """
        imageType:
            [enum] Type of the exported image file
        """

        super().__init__()
        self.imageType = imageType