from ...classes.StiComponentOptions import StiComponentOptions
from ..enums.StiChartRenderType import StiChartRenderType
from ..enums.StiContentAlignment import StiContentAlignment
from ..enums.StiFirstDayOfWeek import StiFirstDayOfWeek
from ..enums.StiHtmlExportMode import StiHtmlExportMode
from ..enums.StiInterfaceType import StiInterfaceType
from ..enums.StiParametersPanelPosition import StiParametersPanelPosition
from ..enums.StiViewerTheme import StiViewerTheme
from ..enums.StiWebUIIconSet import StiWebUIIconSet


class StiAppearanceOptions(StiComponentOptions):
    """A class which controls settings of the viewer appearance."""

### Properties

    @property
    def id(self) -> str:
        return super().id + '.appearance'


### Options

    backgroundColor = 'white'
    """Gets or sets the background color of the viewer."""

    pageBorderColor = 'gray'
    """Gets or sets a color of the report page border."""

    rightToLeft = False
    """Gets or sets a value which controls of output objects in the right to left mode."""

    fullScreenMode = False
    """Gets or sets a value which indicates which indicates that the viewer is displayed in full screen mode."""

    scrollbarsMode = False
    """Gets or sets a value which indicates that the viewer will show the report area with scrollbars."""

    openLinksWindow = '_blank'
    """Gets or sets a browser window to open links from the report."""

    openExportedReportWindow = '_blank'
    """Gets or sets a browser window to open the exported report."""

    showTooltips = True
    """Gets or sets a value which indicates that show or hide tooltips."""

    showTooltipsHelp = True
    """Gets or sets a value which indicates that show or hide the help link in tooltips."""

    showDialogsHelp = True
    """Gets or sets a value which indicates that show or hide the help button in dialogs."""

    pageAlignment = StiContentAlignment.CENTER
    """[enum] Gets or sets the alignment of the viewer page."""

    showPageShadow = False
    """Gets or sets a value which indicates that the shadow of the page will be displayed in the viewer."""

    bookmarksPrint = False
    """Gets or sets a value which allows printing report bookmarks."""

    bookmarksTreeWidth = 180
    """Gets or sets a width of the bookmarks tree in the viewer."""

    parametersPanelPosition = StiParametersPanelPosition.FROM_REPORT
    """[enum] Gets or sets a position of the parameters panel."""

    parametersPanelMaxHeight = 300
    """Gets or sets a max height of parameters panel in the viewer."""

    parametersPanelColumnsCount = 2
    """Gets or sets a count columns in parameters panel."""

    minParametersCountForMultiColumns = 5
    """Gets or sets a minimum count of variables in parameters panel for multi-column display mode."""

    parametersPanelDateFormat = ''
    """Gets or sets a date format for datetime parameters in parameters panel. The default is the client browser date format."""

    parametersPanelSortDataItems = False
    """Gets or sets a value which indicates that variable items will be sorted."""

    interfaceType = StiInterfaceType.AUTO
    """[enum] Gets or sets the type of the viewer interface."""

    chartRenderType = StiChartRenderType.ANIMATED_VECTOR
    """[enum] Gets or sets the type of the chart in the viewer."""

    reportDisplayMode = StiHtmlExportMode.FROM_REPORT
    """[enum] Gets or sets a method how the viewer will show a report."""

    datePickerFirstDayOfWeek = StiFirstDayOfWeek.AUTO
    """[enum] Gets or sets the first day of week in the date picker."""

    datePickerIncludeCurrentDayForRanges = False
    """Gets or sets a value, which indicates that the current day will be included in the ranges of the date picker."""

    allowTouchZoom = True
    """Gets or sets a value which allows touch zoom in the viewer."""

    allowScrollZoom = True
    """Gets or sets a value which allows scroll zoom in the viewer."""

    allowMobileMode = True
    """Gets or sets a value which indicates that allows mobile mode of the viewer interface."""

    combineReportPages = False
    """Gets or sets a value which indicates that if a report contains several pages, then they will be combined in preview."""

    theme = StiViewerTheme.OFFICE_2022_WHITE_BLUE
    """[enum] Gets or sets the current visual theme which is used for drawing visual elements of the viewer."""

    iconSet = StiWebUIIconSet.AUTO
    """[enum] Gets or sets the current icon set for the viewer."""

    allowPropagationEvents = True
    """Gets or sets a value that allows event propagation outside the viewer."""
