import datetime
from typing import List, Optional

from NEMO.models import (
    Consumable,
    Project,
    Reservation,
    StaffCharge,
    Tool,
    User,
)
from NEMO.policy import NEMOPolicy

from NEMO_billing.exceptions import ChargeTypeNotAllowedForProjectException
from NEMO_billing.invoices.models import BillableItemType
from NEMO_billing.prepayments.exceptions import (
    ProjectFundsFacilityNotAllowedException,
    ProjectFundsNotSetException,
    ProjectInsufficientFundsException,
)


# This policy class is not meant to be instantiated directly. It will be used by the generic NEMOBillingPolicy
# See NEMOBillingPolicy for details on how we restrict charge types
class PrepaymentPolicy(NEMOPolicy):
    def check_to_enable_tool(self, tool: Tool, operator: User, user: User, project, staff_charge, remote_work=False):
        billable_type = BillableItemType.STAFF_CHARGE if (staff_charge or remote_work) else BillableItemType.TOOL_USAGE
        self.check_project_prepayment_charge(project, billable_type)

    def check_to_save_reservation(
        self,
        cancelled_reservation: Optional[Reservation],
        new_reservation: Reservation,
        user_creating_reservation: User,
        explicit_policy_override: bool,
    ) -> (List[str], bool):
        charge_type = BillableItemType.TOOL_USAGE if new_reservation.tool else BillableItemType.AREA_ACCESS
        self.check_project_prepayment_charge(new_reservation.project, charge_type)

    def check_billing_to_project(self, project: Project, user: User, item=None, charge=None, *args, **kwargs):
        if hasattr(project, "projectprepaymentdetail"):
            if isinstance(item, StaffCharge):
                self.check_project_prepayment_charge(project, BillableItemType.STAFF_CHARGE)
            self.check_prepayment_allowed_for_core_facility(project, item)
            self.check_prepayment_status_for_project(project)

    def check_prepayment_allowed_for_core_facility(self, project: Project, item):
        only_facilities = project.projectprepaymentdetail.only_core_facilities.all()
        check_item = not isinstance(item, Consumable) or item.core_facility
        if only_facilities and check_item and item.core_facility not in only_facilities:
            raise ProjectFundsFacilityNotAllowedException(project, only_facilities)

    def check_prepayment_status_for_project(self, project: Project):
        # Project has to have prepayments
        if not project.projectprepaymentdetail.fund_set.exists():
            raise ProjectFundsNotSetException(project)
        else:
            prepayment = project.projectprepaymentdetail
            date_to_check = datetime.date.today()
            # This function will raise ProjectFundsExpiredException and ProjectFundsInactiveException
            # At least one prepayment has to be active and not expired
            if not prepayment.active_funds(date_to_check).exists():
                raise ProjectInsufficientFundsException(project)
            else:
                # check total available funds (check since last balance update)
                # we have to check each month separately and calculate available funds and charges
                # otherwise we would miss expiring funds or funds not active yet
                # This method will throw an exception if any month period between dates has insufficient funds
                prepayment.get_prepayment_info(until=date_to_check, raise_exception=True)

    def check_project_prepayment_charge(self, project: Project, billable_item_type: BillableItemType):
        if (
            hasattr(project, "projectprepaymentdetail")
            and billable_item_type not in project.projectprepaymentdetail.billable_charge_types
        ):
            raise ChargeTypeNotAllowedForProjectException(project, billable_item_type)
