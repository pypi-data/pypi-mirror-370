from ...classes.StiComponentOptions import StiComponentOptions


class StiDashboardElementsOptions(StiComponentOptions):
    """A class which controls settings of the dashboardElements."""

### Properties

    @property
    def id(self) -> str:
        return super().id + '.dashboardElements'


### Options

    showTableElement = True
    """Gets or sets a visibility of the TableElement item in the designer."""

    showCardsElement = True
    """Gets or sets a visibility of the CardsElement item in the designer."""

    showChartElement = True
    """Gets or sets a visibility of the ChartElement item in the designer."""

    showGaugeElement = True
    """Gets or sets a visibility of the GaugeElement item in the designer."""

    howPivotTableElement = True
    """Gets or sets a visibility of the PivotTableElement item in the designer."""

    showIndicatorElement = True
    """Gets or sets a visibility of the IndicatorElement item in the designer."""

    showProgressElement = True
    """Gets or sets a visibility of the ProgressElement item in the designer."""

    showRegionMapElement = True
    """Gets or sets a visibility of the RegionMapElement item in the designer."""

    showOnlineMapElement = True
    """Gets or sets a visibility of the OnlineMapElement item in the designer."""

    showImageElement = True
    """Gets or sets a visibility of the ImageElement item in the designer."""

    showWebContentElement = True
    """Gets or sets a visibility of the WebContentElement item in the designer."""

    showTextElement = True
    """Gets or sets a visibility of the TextElement item in the designer."""

    showPanelElement = True
    """Gets or sets a visibility of the PanelElement item in the designer."""

    showShapeElement = True
    """Gets or sets a visibility of the ShapeElement item in the designer."""

    showListBoxElement = True
    """Gets or sets a visibility of the ListBoxElement item in the designer."""

    showComboBoxElement = True
    """Gets or sets a visibility of the ComboBoxElement item in the designer."""

    showTreeViewElement = True
    """Gets or sets a visibility of the TreeViewElement item in the designer."""

    showTreeViewBoxElement = True
    """Gets or sets a visibility of the TreeViewBoxElement item in the designer."""

    showDatePickerElement = True
    """Gets or sets a visibility of the DatePickerElement item in the designer."""

    showButtonElement = True
    """Gets or sets a visibility of the ButtonElement item in the designer."""

    showNumberBoxElement = True
    """Gets or sets a visibility of the NumberBoxElement item in the designer."""