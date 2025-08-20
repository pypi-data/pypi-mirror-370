from ...classes.StiComponentOptions import StiComponentOptions
from ...viewer.enums.StiWebUIIconSet import StiWebUIIconSet
from ..enums.StiDesignerRibbonType import StiDesignerRibbonType
from ..enums.StiDesignerTheme import StiDesignerTheme
from ..enums.StiFirstDayOfWeek import StiFirstDayOfWeek
from ..enums.StiInterfaceType import StiInterfaceType
from ..enums.StiPropertiesGridPosition import StiPropertiesGridPosition
from ..enums.StiReportUnitType import StiReportUnitType
from ..enums.StiWizardType import StiWizardType


class StiAppearanceOptions(StiComponentOptions):
    """A class which controls settings of the designer appearance."""

### Properties

    @property
    def id(self) -> str:
        return super().id + '.appearance'


### Options

    defaultUnit = StiReportUnitType.CENTIMETERS
    """[enum] Gets or sets a default value of unit in the designer."""

    interfaceType = StiInterfaceType.AUTO
    """[enum] Gets or sets the type of the designer interface."""

    showAnimation = True
    """Gets or sets a value which indicates that animation is enabled."""

    showSaveDialog = True
    """Gets or sets a visibility of the save dialog of the designer."""

    showTooltips = True
    """Gets or sets a value which indicates that show or hide tooltips."""

    showTooltipsHelp = True
    """Gets or sets a value which indicates that show or hide tooltips help icon."""

    showDialogsHelp = True
    """Gets or sets a value which indicates that show or hide the help button in dialogs."""

    fullScreenMode = False
    """Gets or sets a value which indicates that the designer is displayed in full screen mode."""

    maximizeAfterCreating = False
    """Gets or sets a value which indicates that the designer will be maximized after creation."""

    showLocalization = True
    """Gets or sets a visibility of the localization control of the designer."""

    allowChangeWindowTitle = True
    """Allow the designer to change the window title."""

    showPropertiesGrid = True
    """Gets or sets a visibility of the properties grid in the designer."""

    showReportTree = True
    """Gets or sets a visibility of the report tree in the designer."""

    propertiesGridPosition = StiPropertiesGridPosition.LEFT
    """[enum] Gets or sets a position of the properties grid in the designer."""

    showSystemFonts = True
    """Gets or sets a visibility of the system fonts in the fonts list."""

    datePickerFirstDayOfWeek = StiFirstDayOfWeek.AUTO
    """[enum] Gets or sets the first day of week in the date picker."""

    undoMaxLevel = 6
    """Gets or sets a maximum level of undo actions with the report. A large number of actions consume more memory on the server side."""

    wizardTypeRunningAfterLoad = StiWizardType.NONE
    """[enum] Gets or sets a value of the wizard type which should be run after designer starts."""

    allowWordWrapTextEditors = True
    """Gets or sets a value which indicates that allows word wrap in the text editors."""

    allowLoadingCustomFontsToClientSide = False
    """Allows loading custom fonts to the client side."""

    formatForDateControls = ''
    """Gets or sets a date format for date controls."""

    enableShortCutKeys = True
    """Gets or sets a value which enables or disables the short cut keys of the designer."""

    defaultRibbonType = StiDesignerRibbonType.CLASSIC
    """[enum] Gets or sets a default value of the ribbon type in the designer."""

    zoom = 100
    """Gets or sets the report showing zoom. The default value is 100."""

    theme = StiDesignerTheme.OFFICE_2022_WHITE_BLUE
    """[enum] Gets or sets the current visual theme which is used for drawing visual elements of the designer."""

    iconSet = StiWebUIIconSet.AUTO
    """[enum] Gets or sets the current icon set for the designer."""

    addCustomAttribute = False
    """Gets or sets a value which enables or disables the attribute component-name for components on the page."""

    allowPropagationEvents = True
    """Gets or sets a value that allows event propagation outside the designer."""
