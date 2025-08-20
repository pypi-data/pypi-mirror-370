from enum import Enum


class StiExportAction(Enum):
    
    NONE = None
    EXPORT_REPORT = 1
    SEND_EMAIL = 2
    PRINT_REPORT = 3
