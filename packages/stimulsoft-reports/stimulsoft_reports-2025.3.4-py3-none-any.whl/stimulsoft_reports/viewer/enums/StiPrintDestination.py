from enum import Enum


class StiPrintDestination(Enum):
    
    DEFAULT = 'Stimulsoft.Viewer.StiPrintDestination.Default'
    PDF = 'Stimulsoft.Viewer.StiPrintDestination.Pdf'
    DIRECT = 'Stimulsoft.Viewer.StiPrintDestination.Direct'
    WITH_PREVIEW = 'Stimulsoft.Viewer.StiPrintDestination.WithPreview'