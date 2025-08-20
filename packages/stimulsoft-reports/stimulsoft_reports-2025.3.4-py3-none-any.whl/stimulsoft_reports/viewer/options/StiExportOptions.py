from ...classes.StiComponentOptions import StiComponentOptions


class StiExportOptions(StiComponentOptions):
    """A class which controls the export options."""
    
### Properties

    @property
    def id(self) -> str:
        return super().id + '.exports'


### Options

    storeExportSettings = True
    """Gets or sets a value which allows store the export settings in the cookies."""

    showExportDialog = True
    """Gets or sets a value which allows to display the export dialog, or to export with the default settings."""

    showExportToDocument = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the report document file."""

    showExportToPdf = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the PDF format."""

    showExportToHtml = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the HTML format."""

    showExportToHtml5 = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the HTML5 format."""

    showExportToWord = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the Word 2007-2024 format."""

    showExportToExcel = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the Excel 2007-2024 format."""

    showExportToCsv = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the CSV format."""

    showExportToJson = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the JSON format."""

    showExportToDbf = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the DBF format."""

    showExportToXml = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the XML format."""

    showExportToDif = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the DIF format."""

    showExportToSylk = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the SYLK format."""

    showExportToText = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the Text format."""

    showExportToOpenDocumentWriter = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the Open Document Text format."""

    showExportToOpenDocumentCalc = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the Open Document Calc format."""

    showExportToPowerPoint = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the HTML format."""

    showExportToImageSvg = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the SVG format."""

    showExportToImagePng = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the PNG format."""

    showExportToImageJpeg = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the JPEG format."""

    showExportToImageSvgz = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the SVGZ format."""

    showExportToImagePcx = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the PCX format."""

    showExportToImageBmp = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the BMP format."""

    showExportToImageGif = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the GIF format."""

    showExportToImageTiff = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the TIFF format."""

    showExportToXps = False
    """Gets or sets a value which indicates that the user can save the report from the viewer to the XPS format."""

    showExportDataOnly = True
    """Gets or sets a value which allows to display the option 'Export Data Only'."""

    showExportToRtf = True
    """Gets or sets a value which indicates that the user can save the report from the viewer to the Rich Text format."""