from enum import Enum


class StiPrintAction(Enum):

    NONE = None
    PRINT_PDF = 'PrintPdf'
    PRINT_WITHOUT_PREVIEW = 'PrintWithoutPreview'
    PRINT_WITH_PREVIEW = 'PrintWithPreview'