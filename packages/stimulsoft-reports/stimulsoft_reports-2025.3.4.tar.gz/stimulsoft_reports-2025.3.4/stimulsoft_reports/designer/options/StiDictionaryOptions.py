from ...classes.StiComponentOptions import StiComponentOptions
from ..enums.StiDesignerPermissions import StiDesignerPermissions
from ..enums.StiNewReportDictionary import StiNewReportDictionary
from ..enums.StiUseAliases import StiUseAliases


class StiDictionaryOptions(StiComponentOptions):
    """A class which controls settings of the dictionary."""

### Properties

    @property
    def id(self) -> str:
        return super().id + '.dictionary'


### Options

    showAdaptersInNewConnectionForm = True
    """Gets or sets a visibility of the other category in the new connection form."""

    showDictionary = True
    """Gets or sets a visibility of the dictionary in the designer."""

    useAliases = StiUseAliases.AUTO
    """[enum] Gets or sets a value which indicates that using aliases in the dictionary."""

    showDictionaryContextMenuProperties = True
    """Gets or sets a visibility of the Properties item in the dictionary context menu."""

    showDictionaryActions = True
    """Gets or sets a visibility of the Actions in the dictionary."""

    newReportDictionary = StiNewReportDictionary.AUTO
    """[enum] Gets or sets a value which indicates what to do with the dictionary when creating a new report in the designer."""

    dataSourcesPermissions = StiDesignerPermissions.ALL
    """[enum] Gets or sets a value of permissions for datasources in the designer."""

    dataTransformationsPermissions = StiDesignerPermissions.ALL
    """[enum] Gets or sets a value of connections for data transformations in the designer."""

    dataConnectionsPermissions = StiDesignerPermissions.ALL
    """[enum] Gets or sets a value of connections for datasources in the designer."""

    dataColumnsPermissions = StiDesignerPermissions.ALL
    """[enum] Gets or sets a value of connections for columns in the designer."""

    dataRelationsPermissions = StiDesignerPermissions.ALL
    """[enum] Gets or sets a value of connections for relations in the designer."""

    businessObjectsPermissions = StiDesignerPermissions.ALL
    """[enum] Gets or sets a value of connections for business objects in the designer."""

    variablesPermissions = StiDesignerPermissions.ALL
    """[enum] Gets or sets a value of connections for variables in the designer."""

    resourcesPermissions = StiDesignerPermissions.ALL
    """[enum] Gets or sets a value of connections for resources in the designer."""