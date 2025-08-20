from enum import Enum


class StiTiffCompressionScheme(Enum):
    """Enumeration for setting compression scheme of the exported Tiff image."""

    DEFAULT = 20
    """Specifies that a multiple-frame file or stream should be closed. Can be passed to the TIFF encoder as a parameter that belongs to the save flag category."""

    LZW = 2
    """Specifies the LZW compression scheme. Can be passed to the TIFF encoder as a parameter that belongs to the Compression category."""

    CCITT3 = 3
    """Specifies the CCITT3 compression scheme. Can be passed to the TIFF encoder as a parameter that belongs to the compression category."""

    CCITT4 = 4
    """Specifies the CCITT4 compression scheme. Can be passed to the TIFF encoder as a parameter that belongs to the compression category."""

    RLE = 5
    """Specifies the RLE compression scheme. Can be passed to the TIFF encoder as a parameter that belongs to the compression category."""

    NONE = 6
    """Specifies no compression. Can be passed to the TIFF encoder as a parameter that belongs to the compression category."""