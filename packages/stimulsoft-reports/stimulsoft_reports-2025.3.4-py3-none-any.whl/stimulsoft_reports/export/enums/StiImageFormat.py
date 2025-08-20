from enum import Enum


class StiImageFormat(Enum):
    """Enumeration for setting format of the exported images."""

    COLOR = 1
    """Images are exported in the color mode."""
    
    GRAYSCALE = 2
    """Images are exported in the grayscale mode."""
    
    MONOCHROME = 3
    """Images are exported in the monochrome mode."""


class ImageFormat(Enum):

    BMP = 0
    #EMF = 1
    #EXIF = 2
    GIF = 3
    #GUID = 4
    #ICON = 5
    JPEG = 6
    #MEMORY_BMP = 7
    PNG = 8
    TIFF = 9
    #WMF = 10