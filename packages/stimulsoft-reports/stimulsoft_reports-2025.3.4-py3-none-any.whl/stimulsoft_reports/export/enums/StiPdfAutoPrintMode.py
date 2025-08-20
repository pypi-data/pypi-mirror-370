from enum import Enum


class StiPdfAutoPrintMode(Enum):
    """Enumeration which sets an AutoPrint mode for pdf files."""

    NONE = 1
    """Do not use AutoPrint feature."""
    
    DIALOG = 2
    """Use printing with print dialog."""
    
    SILENT = 3
    """Use silent printing."""
