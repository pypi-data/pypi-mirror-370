from enum import Enum


class StiWizardType(Enum):

    NONE = 'Stimulsoft.Designer.StiWizardType.None'
    STANDARD_REPORT = 'Stimulsoft.Designer.StiWizardType.StandardReport'
    MASTER_DETAIL_REPORT = 'Stimulsoft.Designer.StiWizardType.MasterDetailReport'
    LABEL_REPORT = 'Stimulsoft.Designer.StiWizardType.LabelReport'
    INVOICES_REPORT = 'Stimulsoft.Designer.StiWizardType.InvoicesReport'
    ORDERS_REPORT = 'Stimulsoft.Designer.StiWizardType.OrdersReport'
    QUOTATION_REPORT = 'Stimulsoft.Designer.StiWizardType.QuotationReport'