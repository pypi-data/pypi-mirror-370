from datetime import datetime, timedelta
from typing import List

from NEMO.models import (
    Area,
    AreaAccessRecord,
    Consumable,
    ConsumableWithdraw,
    Reservation,
    Tool,
    TrainingSession,
    UsageEvent,
    User,
)

from NEMO_billing.invoices.models import BillableItemType
from NEMO_billing.models import CustomCharge
from NEMO_billing.rates.models import Rate, RateCategory, RateType


def create_items() -> (Tool, Area, Consumable, User):
    consumable = Consumable.objects.create(name="Tweezers", quantity=10, reusable=True)
    consumable_type = RateType.objects.get(type="CONSUMABLE")
    rate_category = RateCategory.objects.get(name="Academia")
    Rate.objects.create(category=rate_category, type=consumable_type, consumable=consumable, flat=True, amount="20.00")
    tool = Tool.objects.create(name="Tool", _operational=True)
    tool_type = RateType.objects.get(type="TOOL_USAGE")
    Rate.objects.create(category=rate_category, type=tool_type, tool=tool, amount="30.00")
    area = Area.objects.create(name="Area")
    area_type = RateType.objects.get(type="AREA_USAGE")
    Rate.objects.create(category=rate_category, type=area_type, area=area, amount="40.00")
    staff = User.objects.create(username="staff", first_name="Staff", last_name="Staff", is_staff=True, badge_number=2)
    tool_missed_resa_type = RateType.objects.get(type="TOOL_MISSED_RESERVATION")
    Rate.objects.create(category=rate_category, type=tool_missed_resa_type, tool=tool, amount="15.00")
    tool_training_type = RateType.objects.get(type="TOOL_TRAINING_INDIVIDUAL")
    Rate.objects.create(category=rate_category, type=tool_training_type, tool=tool, amount="10.00")
    staff_charge_type = RateType.objects.get(type="STAFF_CHARGE")
    Rate.objects.create(category=rate_category, type=staff_charge_type, amount="25.00")
    return tool, area, consumable, staff


def delete_all_billables():
    UsageEvent.objects.all().delete()
    AreaAccessRecord.objects.all().delete()
    Reservation.objects.all().delete()
    ConsumableWithdraw.objects.all().delete()
    TrainingSession.objects.all().delete()
    CustomCharge.objects.all().delete()


def get_other_billable_types(types: List[BillableItemType]) -> List[BillableItemType]:
    result = []
    for billableItemType in BillableItemType:
        if billableItemType not in types:
            result.append(billableItemType)
    return result


def add_charges_of_type(test_case, types: List[BillableItemType], end: datetime, cap_eligible_custom_charge=True):
    user, project, staff, tool, area, consumable = (
        test_case.user,
        test_case.project,
        test_case.staff,
        test_case.tool,
        test_case.area,
        test_case.consumable,
    )
    start = end - timedelta(days=1)
    if BillableItemType.TOOL_USAGE in types:
        UsageEvent.objects.create(user=user, operator=user, tool=tool, project=project, start=start, end=end)
    if BillableItemType.CONSUMABLE in types:
        ConsumableWithdraw.objects.create(
            customer=user,
            project=project,
            consumable=consumable,
            quantity=1,
            date=end,
            merchant=staff,
        )
    if BillableItemType.STAFF_CHARGE in types:
        UsageEvent.objects.create(
            user=user, operator=staff, remote_work=True, tool=tool, project=project, start=start, end=end
        )
    if BillableItemType.AREA_ACCESS in types:
        AreaAccessRecord.objects.create(area=area, customer=user, project=project, start=start, end=end)
    if BillableItemType.TRAINING in types:
        TrainingSession.objects.create(
            trainee=user,
            trainer=staff,
            tool=tool,
            project=project,
            date=end,
            duration=30,
            type=TrainingSession.Type.INDIVIDUAL,
        )
    if BillableItemType.MISSED_RESERVATION in types:
        Reservation.objects.create(
            user=user,
            creator=user,
            tool=tool,
            project=project,
            missed=True,
            start=start,
            end=end,
            short_notice=False,
        )
    if BillableItemType.CUSTOM_CHARGE in types:
        CustomCharge.objects.create(
            name="custom",
            customer=user,
            creator=staff,
            project=project,
            date=end,
            amount=10,
            cap_eligible=cap_eligible_custom_charge,
        )
