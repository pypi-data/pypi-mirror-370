from enum import Enum


class StiExcelType(Enum):
    """Enumeration describes a type of the excel exports."""

    EXCEL_BINARY = 1
    """Excel format from Office 97 to Office 2003."""

    EXCEL_XML = 2
    """XML Excel format starts from Office 2003."""

    EXCEL_2007 = 3
    """Excel format starts from Office 2007."""