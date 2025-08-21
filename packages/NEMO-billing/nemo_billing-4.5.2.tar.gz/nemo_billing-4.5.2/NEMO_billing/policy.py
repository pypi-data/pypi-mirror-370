from datetime import date, datetime, time, timedelta
from http import HTTPStatus
from typing import List, Optional, Union

from NEMO.models import (
    Area,
    AreaAccessRecord,
    Consumable,
    ConsumableWithdraw,
    Project,
    Reservation,
    StaffCharge,
    Tool,
    TrainingSession,
    UsageEvent,
    User,
)
from NEMO.policy import NEMOPolicy
from NEMO.utilities import format_datetime
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.timezone import make_aware

from NEMO_billing.exceptions import BillingException, ChargeTypeNotAllowedForProjectException, HardCAPReachedException
from NEMO_billing.invoices.processors import BillableItem
from NEMO_billing.models import ProjectBillingHardCap
from NEMO_billing.utilities import get_billable_item_type_for_item, get_charges_amount_between

try:
    # try to load prepayment policy if installed
    from NEMO_billing.prepayments.policy import PrepaymentPolicy

    prepayment_policy = PrepaymentPolicy()
except:
    prepayment_policy = None

# Some validation for prepayment charges is tricky.
# We want to avoid using signals as they raise a hard exception, and it's challenging to catch it
# So we are using any other method unless we have no choice
# 1. Tool usage, all good we have a policy method containing the project
# 2. Staff charge, all good we can use check_billing_to_project directly
# 3. Area access record is not possible because we don't have the project
# 4. Training we don't have the project either
# 5. Consumables we don't know if those charges are from post usage or not. Either way we cannot separate at the moment
# 6. Custom charges we can use check_billing_to_project
# 7. Missed reservation cannot be dissociated from tool usage or area access
# Bonus: we are also preventing reservation on tool and areas if those are not enabled


# Decided to use signals to prevent any charge not authorized by the fund (see below)
class BillingPolicy(NEMOPolicy):
    def check_to_enable_tool(
        self, tool: Tool, operator: User, user: User, project: Project, staff_charge: bool, remote_work: bool = False
    ):
        response = super().check_to_enable_tool(tool, operator, user, project, staff_charge)
        if response.status_code != HTTPStatus.OK:
            return response
        try:
            if prepayment_policy:
                prepayment_policy.check_to_enable_tool(tool, operator, user, project, staff_charge, remote_work)
        except ChargeTypeNotAllowedForProjectException as e:
            return HttpResponseBadRequest(e.msg)
        return HttpResponse()

    def check_to_save_reservation(
        self,
        cancelled_reservation: Optional[Reservation],
        new_reservation: Reservation,
        user_creating_reservation: User,
        explicit_policy_override: bool,
    ) -> (List[str], bool):
        try:
            if prepayment_policy:
                prepayment_policy.check_to_save_reservation(
                    cancelled_reservation, new_reservation, user_creating_reservation, explicit_policy_override
                )
        except ChargeTypeNotAllowedForProjectException as e:
            return [e.msg], False
        return super().check_to_save_reservation(
            cancelled_reservation, new_reservation, user_creating_reservation, explicit_policy_override
        )

    def check_billing_to_project(
        self,
        project: Project,
        user: User,
        item: Union[Tool, Area, Consumable, StaffCharge] = None,
        charge: Union[UsageEvent, AreaAccessRecord, ConsumableWithdraw, StaffCharge, Reservation] = None,
        *args,
        **kwargs,
    ):
        super().check_billing_to_project(project, user, item, charge, *args, **kwargs)

        if isinstance(charge, Reservation):
            project_details = getattr(project, "projectbillingdetails", None)

            if project_details and project_details.expires_on:
                expiration_datetime = datetime.combine(
                    project_details.expires_on + timedelta(days=1), time.min
                ).astimezone()
                if charge.end > expiration_datetime:
                    project_expiration_exception = BillingException(
                        f'Your project "{project.name}" expires on {format_datetime(expiration_datetime)} which is before your reservation end date'
                    )
                    project_expiration_exception.project = project
                    project_expiration_exception.user = charge.user
                    raise project_expiration_exception

        if prepayment_policy:
            prepayment_policy.check_billing_to_project(project, user, item, charge)
        if hasattr(project, "projectbillinghardcap_set"):
            self.check_hard_cap_status_for_project(project, charge)

    def check_hard_cap_status_for_project(self, project: Project, charge):
        # We need to check that the new charge time is within the hard cap daterange
        # and that the type is in the list of CAP charges
        hard_caps = project.projectbillinghardcap_set.filter(enabled=True)
        if hard_caps:
            if charge and charge.get_start() and charge.get_end():
                start = charge.get_start().astimezone()
                end = charge.get_end().astimezone()
                hard_caps = hard_caps.exclude(start_date__lt=start, end_date__lt=start).exclude(
                    start_date__gt=end, end_date__gt=end
                )
            else:
                # If there is no charge let's use right now as the time
                charge_date = (charge.get_start() or charge.get_end()) if charge else datetime.now()
                charge_date = charge_date.astimezone()
                hard_caps = hard_caps.filter(Q(start_date__lte=charge_date.date()) | Q(start_date__isnull=True)).filter(
                    Q(end_date__gte=charge_date.date()) | Q(end_date__isnull=True)
                )
            for hard_cap in hard_caps:
                if get_billable_item_type_for_item(charge) in hard_cap.billable_charge_types:
                    hard_cap: ProjectBillingHardCap = hard_cap
                    start_datetime = make_aware(datetime.combine(hard_cap.start_date or date.min, time.min))
                    end_datetime = make_aware(datetime.combine(hard_cap.end_date or date.max, time.max))
                    charges, amount = get_charges_amount_between(
                        hard_cap.project,
                        hard_cap.configuration,
                        start_datetime,
                        end_datetime,
                        hard_cap.billable_charge_types,
                    )
                    if amount > hard_cap.amount:
                        raise HardCAPReachedException(hard_cap)


@receiver(models.signals.pre_save)
def auto_check_charge_type_for_projects(
    sender, instance: Union[AreaAccessRecord, UsageEvent, TrainingSession, StaffCharge], **kwargs
):
    # We don't need consumable withdrawals and reservations because we dealt with them in the policy
    if not issubclass(sender, (AreaAccessRecord, UsageEvent, TrainingSession, StaffCharge)):
        return
    if not instance.pk:
        if prepayment_policy:
            prepayment_policy.check_project_prepayment_charge(
                instance.project, BillableItem(instance, instance.project).item_type
            )
