import urllib.parse

from ...classes.StiComponentOptions import StiComponentOptions
from ...viewer.options.StiViewerOptions import StiViewerOptions
from .StiAppearanceOptions import StiAppearanceOptions
from .StiBandsOptions import StiBandsOptions
from .StiCrossBandsOptions import StiCrossBandsOptions
from .StiDashboardElementsOptions import StiDashboardElementsOptions
from .StiDictionaryOptions import StiDictionaryOptions
from .StiReportComponentsOptions import StiReportComponentsOptions
from .StiToolbarOptions import StiToolbarOptions


class StiDesignerOptions(StiComponentOptions):
    """A class which controls settings of the designer."""

### Properties

    __localization: str = None
    
    @property
    def localization(self) -> str:
        """Gets or sets a path to the localization file for the designer."""
        
        return self.__localization
    
    @localization.setter
    def localization(self, value: str):
        self.__localization = value

    __localizations: list[str] = []

    @property
    def localizations(self) -> list[str]:
        self.__localizations = list(set(self.__localizations))
        return self.__localizations
    
    @localizations.setter
    def localizations(self, value: list[str]):
        self.__localizations = value


### Options

    appearance: StiAppearanceOptions = None
    """A class which controls settings of the designer appearance."""

    toolbar: StiToolbarOptions = None
    """A class which controls settings of the designer toolbar."""

    bands: StiBandsOptions = None
    """A class which controls settings of the bands."""

    crossBands: StiCrossBandsOptions = None
    """A class which controls settings of the cross-bands."""

    components: StiReportComponentsOptions = None
    """A class which controls settings of the report components."""

    dashboardElements: StiDashboardElementsOptions = None
    """A class which controls settings of the dashboard elements."""

    dictionary: StiDictionaryOptions = None
    """A class which controls settings of the dictionary."""

    width = '100%'
    """Gets or sets the width of the designer."""

    height = '800px'
    """Gets or sets the height of the designer."""

    viewerOptions: StiViewerOptions = None
    """A class which controls settings of the preview window."""


### Public

    def addLocalization(self, path):
        """Adds localization to the designer menu."""

        self.localizations.append(path)
    
    def getHtml(self):
        result = ''

        for localization in self.localizations:
            localizationPath = self.getLocalizationPath(urllib.parse.quote(localization))
            if localizationPath != None and localization != self.localization:
                result += f"Stimulsoft.Base.Localization.StiLocalization.addLocalizationFile('{localizationPath}', true);\n"

        localizationPath = self.getLocalizationPath(self.localization)
        if localizationPath:
            result += f"Stimulsoft.Base.Localization.StiLocalization.setLocalizationFile('{localizationPath}');\n"

        result += f'let {self.id} = new Stimulsoft.Designer.StiDesignerOptions();\n'

        return result + super().getHtml()
    

### Constructor

    def __init__(self):
        self.appearance = StiAppearanceOptions()
        self.toolbar = StiToolbarOptions()
        self.bands = StiBandsOptions()
        self.crossBands = StiCrossBandsOptions()
        self.components = StiReportComponentsOptions()
        self.dashboardElements = StiDashboardElementsOptions()
        self.dictionary = StiDictionaryOptions()
        self.viewerOptions = StiViewerOptions()