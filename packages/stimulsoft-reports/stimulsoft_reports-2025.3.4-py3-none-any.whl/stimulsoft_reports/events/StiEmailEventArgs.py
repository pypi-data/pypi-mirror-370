from ..classes.StiEmailSettings import StiEmailSettings
from .StiExportEventArgs import StiExportEventArgs


class StiEmailEventArgs(StiExportEventArgs):
    
    settings: StiEmailSettings = None
    """Settings for sending the exported report by Email."""
    