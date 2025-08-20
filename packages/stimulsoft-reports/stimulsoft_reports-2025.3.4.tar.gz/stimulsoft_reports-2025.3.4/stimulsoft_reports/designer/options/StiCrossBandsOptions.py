from ...classes.StiComponentOptions import StiComponentOptions


class StiCrossBandsOptions(StiComponentOptions):
    """A class which controls settings of the cross-bands."""

### Properties

    @property
    def id(self) -> str:
        return super().id + '.crossBands'


### Options

    showCrossTab = True
    """Gets or sets a visibility of the CrossTab item in the crossbands menu of the designer."""

    showCrossGroupHeaderBand = True
    """Gets or sets a visibility of the CrossGroupHeaderBand item in the crossbands menu of the designer."""

    showCrossGroupFooterBand = True
    """Gets or sets a visibility of the CrossGroupFooterBand item in the crossbands menu of the designer."""

    showCrossHeaderBand = True
    """Gets or sets a visibility of the CrossHeaderBand item in the crossbands menu of the designer."""

    showCrossFooterBand = True
    """Gets or sets a visibility of the CrossFooterBand item in the crossbands menu of the designer."""

    showCrossDataBand = True
    """Gets or sets a visibility of the CrossDataBand item in the crossbands menu of the designer."""