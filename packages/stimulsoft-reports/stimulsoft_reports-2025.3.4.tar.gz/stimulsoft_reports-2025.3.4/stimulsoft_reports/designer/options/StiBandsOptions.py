from ...classes.StiComponentOptions import StiComponentOptions


class StiBandsOptions(StiComponentOptions):
    """A class which controls settings of the bands."""

### Properties

    @property
    def id(self) -> str:
        return super().id + '.bands'


### Options

    showReportTitleBand = True
    """Gets or sets a visibility of the ReportTitleBand item in the bands menu of the designer."""

    showReportSummaryBand = True
    """Gets or sets a visibility of the ReportSummaryBand item in the bands menu of the designer."""

    showPageHeaderBand = True
    """Gets or sets a visibility of the PageHeaderBand item in the bands menu of the designer."""

    showPageFooterBand = True
    """Gets or sets a visibility of the PageFooterBand item in the bands menu of the designer."""

    showGroupHeaderBand = True
    """Gets or sets a visibility of the GroupHeaderBand item in the bands menu of the designer."""

    showGroupFooterBand = True
    """Gets or sets a visibility of the GroupFooterBand item in the bands menu of the designer."""

    showHeaderBand = True
    """Gets or sets a visibility of the HeaderBand item in the bands menu of the designer."""

    showFooterBand = True
    """Gets or sets a visibility of the FooterBand item in the bands menu of the designer."""

    showColumnHeaderBand = True
    """Gets or sets a visibility of the ColumnHeaderBand item in the bands menu of the designer."""

    showColumnFooterBand = True
    """Gets or sets a visibility of the ColumnFooterBand item in the bands menu of the designer."""

    showDataBand = True
    """Gets or sets a visibility of the DataBand item in the bands menu of the designer."""

    showHierarchicalBand = True
    """Gets or sets a visibility of the HierarchicalBand item in the bands menu of the designer."""

    showChildBand = True
    """Gets or sets a visibility of the ChildBand item in the bands menu of the designer."""

    showEmptyBand = True
    """Gets or sets a visibility of the EmptyBand item in the bands menu of the designer."""

    showOverlayBand = True
    """Gets or sets a visibility of the OverlayBand item in the bands menu of the designer."""

    showTable = True
    """Gets or sets a visibility of the Table item in the bands menu of the designer."""

    showTableOfContents = True
    """Gets or sets a visibility of the TableOfContents item in the Bands menu of the designer."""