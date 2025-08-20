from ...classes.StiComponentOptions import StiComponentOptions
from ..enums.StiContentAlignment import StiContentAlignment
from ..enums.StiPrintDestination import StiPrintDestination
from ..enums.StiShowMenuMode import StiShowMenuMode
from ..enums.StiToolbarDisplayMode import StiToolbarDisplayMode
from ..enums.StiWebViewMode import StiWebViewMode


class StiToolbarOptions(StiComponentOptions):
    """A class which controls settings of the viewer toolbar."""

### Properties

    @property
    def id(self) -> str:
        return super().id + '.toolbar'


### Options

    visible = True
    """Gets or sets a value which indicates that toolbar will be shown in the viewer."""

    displayMode = StiToolbarDisplayMode.SIMPLE
    """[enum] Gets or sets the display mode of the toolbar - simple or separated into upper and lower parts."""

    backgroundColor = 'transparent'
    """Gets or sets a color of the toolbar background. The default value is the theme color."""

    borderColor = 'transparent'
    """Gets or sets a color of the toolbar border. The default value is the theme color."""

    fontColor = 'transparent'
    """Gets or sets a color of the toolbar texts."""

    fontFamily = 'Arial'
    """Gets or sets a value which indicates which font family will be used for drawing texts in the viewer."""

    alignment = StiContentAlignment.DEFAULT
    """[enum] Gets or sets the alignment of the viewer toolbar."""

    showButtonCaptions = True
    """Gets or sets a value which allows displaying or hiding toolbar buttons captions."""

    showPrintButton = True
    """Gets or sets a visibility of the Print button in the toolbar of the viewer."""

    showOpenButton = True
    """Gets or sets a visibility of the Open button in the toolbar of the viewer."""

    showSaveButton = True
    """Gets or sets a visibility of the Save button in the toolbar of the viewer."""

    showSendEmailButton = False
    """Gets or sets a visibility of the Send Email button in the toolbar of the viewer."""

    showFindButton = True
    """Gets or sets a visibility of the Find button in the toolbar of the viewer."""

    showSignatureButton = True
    """Gets or sets a visibility of the Signature button in the toolbar of the viewer."""

    showBookmarksButton = True
    """Gets or sets a visibility of the Bookmarks button in the toolbar of the viewer."""

    showParametersButton = True
    """Gets or sets a visibility of the Parameters button in the toolbar of the viewer."""

    showResourcesButton = True
    """Gets or sets a visibility of the Resources button in the toolbar of the viewer."""

    showEditorButton = True
    """Gets or sets a visibility of the Editor button in the toolbar of the viewer."""

    showFullScreenButton = True
    """Gets or sets a visibility of the Full Screen button in the toolbar of the viewer."""

    showRefreshButton = True
    """Gets or sets a visibility of the Refresh button in the toolbar of the viewer."""

    showFirstPageButton = True
    """Gets or sets a visibility of the First Page button in the toolbar of the viewer."""

    showPreviousPageButton = True
    """Gets or sets a visibility of the Prev Page button in the toolbar of the viewer."""

    showCurrentPageControl = True
    """Gets or sets a visibility of the current page control in the toolbar of the viewer."""

    showNextPageButton = True
    """Gets or sets a visibility of the Next Page button in the toolbar of the viewer."""

    showLastPageButton = True
    """Gets or sets a visibility of the Last Page button in the toolbar of the viewer."""

    showZoomButton = True
    """Gets or sets a visibility of the Zoom control in the toolbar of the viewer."""

    showViewModeButton = True
    """Gets or sets a visibility of the View Mode button in the toolbar of the viewer."""

    showDesignButton = False
    """Gets or sets a visibility of the Design button in the toolbar of the viewer."""

    showAboutButton = True
    """Gets or sets a visibility of the About button in the toolbar of the viewer."""

    showPinToolbarButton = True
    """Gets or sets a visibility of the Pin button in the toolbar of the viewer in mobile mode."""

    printDestination = StiPrintDestination.DEFAULT
    """[enum] Gets or sets the default mode of the report print destination."""

    viewMode = StiWebViewMode.SINGLE_PAGE
    """[enum] Gets or sets the mode of showing a report in the viewer - one page or the whole report."""

    zoom = 100
    """Gets or sets the report showing zoom. The default value is 100."""

    menuAnimation = True
    """Gets or sets a value which indicates that menu animation is enabled."""

    showMenuMode = StiShowMenuMode.CLICK
    """[enum] Gets or sets the mode that shows menu of the viewer."""

    autoHide = False
    """Gets or sets a value which allows automatically hide the viewer toolbar in mobile mode."""