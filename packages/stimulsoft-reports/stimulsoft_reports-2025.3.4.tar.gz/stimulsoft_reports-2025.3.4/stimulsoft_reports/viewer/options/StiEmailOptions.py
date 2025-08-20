from ...classes.StiComponentOptions import StiComponentOptions


class StiEmailOptions(StiComponentOptions):
    """A class which controls the export options."""

### Properties

    @property
    def id(self) -> str:
        return super().id + '.email'


### Options
    
    showEmailDialog = True
    """Gets or sets a value which allows to display the Email dialog, or send Email with the default settings."""

    showExportDialog = True
    """Gets or sets a value which allows to display the export dialog for Email, or export report for Email with the default settings."""

    defaultEmailAddress = ''
    """Gets or sets the default email address of the message created in the viewer."""

    defaultEmailSubject = ''
    """Gets or sets the default subject of the message created in the viewer."""

    defaultEmailMessage = ''
    """Gets or sets the default text of the message created in the viewer."""