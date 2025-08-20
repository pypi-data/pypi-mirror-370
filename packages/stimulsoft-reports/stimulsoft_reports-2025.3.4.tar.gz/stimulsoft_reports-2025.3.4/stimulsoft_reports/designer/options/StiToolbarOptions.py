from ...classes.StiComponentOptions import StiComponentOptions


class StiToolbarOptions(StiComponentOptions):
    """A class which controls settings of the designer toolbar."""

### Properties

    @property
    def id(self) -> str:
        return super().id + '.toolbar'


### Options

    visible = True
    """Gets or sets a value which indicates that toolbar will be shown in the designer."""

    showPreviewButton = True
    """Gets or sets a visibility of the preview button in the toolbar of the designer."""

    showSaveButton = False
    """Gets or sets a visibility of the save button in the toolbar of the designer."""

    showAboutButton = False
    """Gets or sets a visibility of the about button in the toolbar of the designer."""

    showFileMenu = True
    """Gets or sets a visibility of the file menu of the designer."""

    showFileMenuNew = True
    """Gets or sets a visibility of the item New in the file menu."""

    showFileMenuOpen = True
    """Gets or sets a visibility of the item Open in the file menu."""

    showFileMenuSave = True
    """Gets or sets a visibility of the item Save in the file menu."""

    showFileMenuSaveAs = True
    """Gets or sets a visibility of the item Save As in the file menu."""

    showFileMenuClose = True
    """Gets or sets a visibility of the item Close in the file menu."""

    showFileMenuExit = False
    """Gets or sets a visibility of the item Exit in the file menu."""

    showFileMenuReportSetup = True
    """Gets or sets a visibility of the item Report Setup in the file menu."""

    showFileMenuOptions = True
    """Gets or sets a visibility of the item Options in the file menu."""

    showFileMenuInfo = True
    """Gets or sets a visibility of the item Info in the file menu."""

    showFileMenuAbout = True
    """Gets or sets a visibility of the item About in the file menu."""

    showFileMenuNewReport = True
    """Gets or sets a visibility of the new report button in the file menu."""

    showFileMenuNewDashboard = True
    """Gets or sets a visibility of the new dashboard button in the file menu."""

    showSetupToolboxButton = True
    """Gets or sets a visibility of the setup toolbox button in the designer."""

    showNewPageButton = True
    """Gets or sets a visibility of the new page button in the designer."""

    showNewDashboardButton = True
    """Gets or sets a visibility of the new dashboard button in the designer."""