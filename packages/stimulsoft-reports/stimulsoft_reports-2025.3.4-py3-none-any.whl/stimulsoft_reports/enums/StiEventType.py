from enum import Enum


class StiEventType(Enum):

    NONE = None
    GET_RESOURCE = 'GetResource'
    PREPARE_VARIABLES = 'PrepareVariables'
    DATABASE_CONNECT = 'DatabaseConnect'
    BEGIN_PROCESS_DATA = 'BeginProcessData'
    END_PROCESS_DATA = 'EndProcessData'
    BEFORE_RENDER = 'BeforeRender'
    CREATE_REPORT = 'CreateReport'
    OPEN_REPORT = 'OpenReport'
    OPENED_REPORT = 'OpenedReport'
    SAVE_REPORT = 'SaveReport'
    SAVE_AS_REPORT = 'SaveAsReport'
    PRINT_REPORT = 'PrintReport'
    BEGIN_EXPORT_REPORT = 'BeginExportReport'
    END_EXPORT_REPORT = 'EndExportReport'
    EMAIL_REPORT = 'EmailReport'
    INTERACTION = 'Interaction'
    DESIGN_REPORT = 'DesignReport'
    PREVIEW_REPORT = 'PreviewReport'
    CLOSE_REPORT = 'CloseReport'
    EXIT = 'Exit'


### Helpers

    @staticmethod
    def getValues():
        return [enum.value for enum in StiEventType if enum.value != None]
