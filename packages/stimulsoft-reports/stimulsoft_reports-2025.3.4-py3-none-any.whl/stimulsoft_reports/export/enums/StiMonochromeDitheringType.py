from enum import Enum


class StiMonochromeDitheringType(Enum):
    """Enumeration describes a type of dithering for monochrome PCX file."""

    NONE = 1
    """Without dithering. Low quality, small size of file."""
    
    FLOYD_STEINBERG = 2
    """Floyd-Steinberg dithering. Good quality, big size of file."""
    
    ORDERED = 3
    """Ordered dithering with Bayer matrix 4x4. Poor quality, medium size of file."""