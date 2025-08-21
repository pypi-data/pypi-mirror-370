from NEMO.exceptions import ProjectChargeException
from NEMO.utilities import format_daterange, format_datetime

from NEMO_billing.invoices.models import BillableItemType
from NEMO_billing.invoices.utilities import display_amount
from NEMO_billing.models import ProjectBillingHardCap


# General billing exception class
class BillingException(ProjectChargeException):
    def __init__(self, msg=None):
        project = getattr(self, "project", None)
        user = getattr(self, "user", None)
        super().__init__(project, user, msg)


class ChargeTypeNotAllowedForProjectException(BillingException):
    def __init__(self, project, charge_type: BillableItemType, msg=None):
        self.charge_type = charge_type
        new_msg = f"{charge_type.friendly_display_name()} charges are not allowed for project {project.name}"
        super().__init__(msg or new_msg)


class HardCAPReachedException(BillingException):
    def __init__(self, project_hard_cap: ProjectBillingHardCap, msg=None):
        self.project_hard_cap = project_hard_cap
        date_range_display = ""
        if project_hard_cap.start_date and project_hard_cap.end_date:
            date_range_display = f" during the period {format_daterange(project_hard_cap.start_date, project_hard_cap.end_date, d_format='SHORT_DATE_FORMAT')}"
        elif project_hard_cap.start_date:
            date_range_display = f" since {format_datetime(project_hard_cap.start_date, df='SHORT_DATE_FORMAT')}"
        elif project_hard_cap.end_date:
            date_range_display = f" until {format_datetime(project_hard_cap.end_date, df='SHORT_DATE_FORMAT')}"
        new_msg = f"You reached the maximum amount allowed of {display_amount(project_hard_cap.amount, project_hard_cap.configuration)} for this project{date_range_display}"
        self.project = project_hard_cap.project
        super().__init__(msg or new_msg)
