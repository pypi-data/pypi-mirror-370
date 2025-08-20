from ...classes.StiComponentOptions import StiComponentOptions
from ...enums.StiComponentType import StiComponentType
from .StiAppearanceOptions import StiAppearanceOptions
from .StiEmailOptions import StiEmailOptions
from .StiExportOptions import StiExportOptions
from .StiToolbarOptions import StiToolbarOptions


class StiViewerOptions(StiComponentOptions):
    """A class which controls settings of the viewer."""

### Private

    __localization: str = None


### Properties

    @property
    def id(self) -> str:
        return super().id + '.viewerOptions' if self.isPreviewControl else super().id
    
    @property
    def localization(self) -> str:
        """Gets or sets a path to the localization file for the viewer."""
        
        return self.__localization
    
    @localization.setter
    def localization(self, value: str):
        self.__localization = value
    
    @property
    def isPreviewControl(self) -> bool:
        return self.component.componentType == StiComponentType.DESIGNER


### Options

    appearance: StiAppearanceOptions = None
    """A class which controls settings of the viewer appearance."""

    toolbar: StiToolbarOptions = None
    """A class which controls settings of the viewer toolbar."""

    exports: StiExportOptions = None
    """A class which controls the export options."""

    email: StiEmailOptions = None
    """A class which controls the export options."""

    width = '100%'
    """Gets or sets the width of the viewer."""

    height = ''
    """Gets or sets the height of the viewer."""


### Public

    def getHtml(self) -> str:
        
        if self.isPreviewControl:
            return super().getHtml()

        result = ''

        localizationPath: str = self.getLocalizationPath(self.localization)
        if localizationPath:
            result += f"Stimulsoft.Base.Localization.StiLocalization.setLocalizationFile('{localizationPath}');\n"

        result += f'let {self.id} = new Stimulsoft.Viewer.StiViewerOptions();\n'

        return result + super().getHtml()


### Constructor

    def __init__(self):
        self.appearance = StiAppearanceOptions()
        self.toolbar = StiToolbarOptions()
        self.exports = StiExportOptions()
        self.email = StiEmailOptions()
        