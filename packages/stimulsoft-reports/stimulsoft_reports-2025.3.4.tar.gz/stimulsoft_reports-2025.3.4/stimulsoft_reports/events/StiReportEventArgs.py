import copy
import json

from stimulsoft_data_adapters.classes.StiFunctions import StiFunctions
from stimulsoft_data_adapters.events.StiEventArgs import StiEventArgs


class StiReportEventArgs(StiEventArgs):

### Fields

    __report: object = None


### Properties

    @property
    def report(self) -> object:
        """The current report JSON object with the set of all properties."""

        return self.__report
    
    @report.setter
    def report(self, value: object):
        self.__report = copy.deepcopy(value)
    
    fileName: str = None
    """The name of the report file to save."""

    isWizardUsed: bool = None
    """A flag indicating that the wizard was used when creating the report."""

    autoSave: bool = None
    """A flag indicating that the report was saved automatically."""

    data: list = None
    """Predefined data object for building the report. Please use the 'regReportData()' method to set it."""


### Methods

    def regReportData(self, name: str, data: object, synchronize: bool = False):
        """
        Sets the data that will be passed to the report generator before building the report.
        It can be an XML or JSON string, as well as an array or a data object that will be serialized into a JSON string.

        name:
            The name of the data source in the report.

        data:
            Report data as a string, array, or object.

        synchronize:
            If true, data synchronization will be called after the data is registered.
        """

        stringData = data if type(data) == str else json.dumps(data)
        if not StiFunctions.isNullOrEmpty(stringData):
            self.data = {
                'name': name,
                'data': stringData,
                'synchronize': synchronize
            }
