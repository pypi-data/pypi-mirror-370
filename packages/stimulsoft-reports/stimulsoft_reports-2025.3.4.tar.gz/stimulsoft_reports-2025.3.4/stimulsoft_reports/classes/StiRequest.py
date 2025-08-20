import json

from stimulsoft_data_adapters.classes.StiBaseRequest import StiBaseRequest

from ..enums import StiEventType
from ..enums.Encoding import Encoding


class StiRequest(StiBaseRequest):

### Properties

    event = StiEventType.NONE
    sender: object = None
    data: str = None
    fileName: str = None
    action: str = None
    printAction: str = None
    format: str = None
    formatName: str = None
    settings: dict = None
    variables: str = None
    isWizardUsed: bool = None
    report: str = None
    autoSave: bool = None
    pageRange: object = None
    reportType: int = None


### Helpers

    def _setProperty(self, name, value):
        if name == 'report' or name == 'settings':
            setattr(self, name, json.loads(value) if value != None else None)

            if name == 'settings' and 'encoding' in self.settings:
                encoding: dict = self.settings.get('encoding')
                encodingName: str = encoding.get('encodingName')
                self.settings['encoding'] = Encoding.getByName(encodingName)
        else:
            super()._setProperty(name, value)

    """def checkRequestParams(self, obj: object):
        if (not obj.event is None and (obj.command == StiDataCommand.TEST_CONNECTION or StiDataCommand.EXECUTE_QUERY)):
            self.event = StiEventType.BEGIN_PROCESS_DATA

        if (obj.report):
            self.report = obj.report
            self.reportJson = json_encode(self.report)

        return StiResult.success(None, self)"""