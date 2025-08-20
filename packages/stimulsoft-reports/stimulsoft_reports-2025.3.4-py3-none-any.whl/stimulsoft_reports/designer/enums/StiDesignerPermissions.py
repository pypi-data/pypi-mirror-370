from enum import Enum


class StiDesignerPermissions(Enum):

    NONE = 'Stimulsoft.Designer.StiDesignerPermissions.None'
    CREATE = 'Stimulsoft.Designer.StiDesignerPermissions.Create'
    DELETE = 'Stimulsoft.Designer.StiDesignerPermissions.Delete'
    MODIFY = 'Stimulsoft.Designer.StiDesignerPermissions.Modify'
    VIEW = 'Stimulsoft.Designer.StiDesignerPermissions.View'
    MODIFY_VIEW = 'Stimulsoft.Designer.StiDesignerPermissions.ModifyView'
    ALL = 'Stimulsoft.Designer.StiDesignerPermissions.All'