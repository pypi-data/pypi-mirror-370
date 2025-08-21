from NEMO.models import Area, Consumable, Project, Tool

from NEMO_billing.exceptions import BillingException
from NEMO_billing.invoices.models import Invoice, InvoiceDetailItem
from NEMO_billing.rates.models import RateCategory, RateType


class NoRateSetException(BillingException):
    def __init__(
        self,
        rate_type: RateType,
        category: RateCategory = None,
        tool: Tool = None,
        area: Area = None,
        consumable: Consumable = None,
    ):
        self.rate_type = rate_type
        self.category = category
        self.tool = tool
        self.area = area
        self.consumable = consumable
        for_category = f" for category: {category}" if category else ""
        for_item = (
            f" for: {tool if tool else area if area else consumable if consumable else ''}"
            if tool or area or consumable
            else ""
        )
        msg = f"No {self.rate_type.get_type_display()} rate is set{for_item}{for_category}"
        super().__init__(msg)


class NoProjectCategorySetException(BillingException):
    def __init__(self, rate_type: RateType, project: Project):
        self.rate_type = rate_type
        self.project = project
        msg = f"{self.rate_type.get_type_display()} is category specific but no category is set on project {project}"
        super().__init__(msg)


class NoProjectDetailsSetException(BillingException):
    def __init__(self, project: Project):
        self.project = project
        msg = f"There are no project details set for project {project}"
        super().__init__(msg)


class InvoiceAlreadyExistException(BillingException):
    def __init__(self, invoice: Invoice):
        self.invoice = invoice
        msg = f"An invoice ({invoice.invoice_number}) already exist for this project for this date range. Void it to be able to generate it again"
        super().__init__(msg)


class InvoiceItemsNotInFacilityException(BillingException):
    def __init__(self, item: InvoiceDetailItem):
        self.item = item
        item_type_display = item.get_item_type_display().replace("_", " ")
        msg = f"Error generating invoice. A {item_type_display}: {item.name} for user {item.user} is not part of any core facilities"
        super().__init__(msg)


class InvoiceGenerationException(BillingException):
    def __init__(self, invoice: Invoice, renderer, e: Exception):
        self.invoice = invoice
        self.renderer = renderer
        msg = f"Error rendering invoice {invoice.invoice_number} with {renderer.__class__.__name__} for project {invoice.project_details.project_name}: {str(e)}."
        super().__init__(msg)
