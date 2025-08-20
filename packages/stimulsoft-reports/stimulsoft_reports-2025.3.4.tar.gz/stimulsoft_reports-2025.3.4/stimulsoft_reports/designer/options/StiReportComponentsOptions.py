from ...classes.StiComponentOptions import StiComponentOptions


class StiReportComponentsOptions(StiComponentOptions):
    """A class which controls settings of the components."""

### Properties

    @property
    def id(self) -> str:
        return super().id + '.components'


### Options

    showText = True
    """Gets or sets a visibility of the Text item in the components menu of the designer."""

    showTextInCells = True
    """Gets or sets a visibility of the TextInCells item in the components menu of the designer."""

    showRichText = False
    """Gets or sets a visibility of the RichText item in the components menu of the designer."""

    showImage = True
    """Gets or sets a visibility of the Image item in the components menu of the designer."""

    showBarCode = True
    """Gets or sets a visibility of the BarCode item in the components menu of the designer."""

    showShape = True
    """Gets or sets a visibility of the Shape item in the components menu of the designer."""

    showPanel = True
    """Gets or sets a visibility of the Panel item in the components menu of the designer."""

    showClone = True
    """Gets or sets a visibility of the Clone item in the components menu of the designer."""

    showCheckBox = True
    """Gets or sets a visibility of the CheckBox item in the components menu of the designer."""

    showSubReport = True
    """Gets or sets a visibility of the SubReport item in the components menu of the designer."""

    showZipCode = False
    """Gets or sets a visibility of the ZipCode item in the components menu of the designer."""

    showChart = True
    """Gets or sets a visibility of the Chart item in the components menu of the designer."""

    showGauge = True
    """Gets or sets a visibility of the Gauge item in the components menu of the designer."""

    showSparkline = True
    """Gets or sets a visibility of the Sparkline item in the components menu of the designer."""

    showMathFormula = False
    """Gets or sets a visibility of the MathFormula item in the Components menu of the designer."""

    showMap = True
    """Gets or sets a visibility of the Map item in the Components menu of the designer."""

    showElectronicSignature = True
    """Gets or sets a visibility of the Electronic Signature item in the Components menu of the designer."""

    showPdfDigitalSignature = True
    """Gets or sets a visibility of the PdfDigitalSignature item in the Components menu of the designer."""

    showHorizontalLinePrimitive = True
    """Gets or sets a visibility of the Horizontal Line Primitive item in the Components menu of the designer."""

    showVerticalLinePrimitive = True
    """Gets or sets a visibility of the Vertical Line Primitive item in the Components menu of the designer."""

    showRectanglePrimitive = True
    """Gets or sets a visibility of the Rectangle Primitive item in the Components menu of the designer."""

    showRoundedRectanglePrimitive = True
    """Gets or sets a visibility of the Rounded Rectangle Primitive item in the Components menu of the designer."""