from enum import Enum


class StiPdfImageCompressionMethod(Enum):
    """Enumeration which sets an image compression method for PDF export."""

    JPEG = 1
    """A Jpeg method (DCTDecode) will be used for the exporting of the rendered document."""
    
    FLATE = 2
    """A Flate method (FlateDecode) will be used for the exporting of the rendered document."""
    
    INDEXED = 3
    """A Indexed method (IndexedColors + FlateDecode) will be used for the exporting of the rendered document."""