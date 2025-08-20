from enum import Enum


class StiPdfZUGFeRDComplianceMode(Enum):
    """Enumeration for setting modes of ZUGFeRD compliance."""

    NONE = 0
    V1 = 1
    V2 = 2
    V2_1 = 3