from enum import Enum


class StiImageType(Enum):
    """Enumeration describes a type of the images for the exports."""

    BMP = 1
    GIF = 2
    JPEG = 3
    PCX = 4
    PNG = 5
    TIFF = 6
    #EMF = 7
    SVG = 8
    SVGZ = 9