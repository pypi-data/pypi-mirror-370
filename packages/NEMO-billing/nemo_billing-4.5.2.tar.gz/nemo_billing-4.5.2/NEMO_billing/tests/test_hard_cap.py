import datetime
from datetime import timedelta
from http import HTTPStatus

from NEMO.models import AreaAccessRecord, ConsumableWithdraw, Reservation, StaffCharge, TrainingSession, UsageEvent
from NEMO.policy import policy_class as policy
from NEMO.utilities import get_month_timeframe
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from NEMO_billing.exceptions import HardCAPReachedException
from NEMO_billing.invoices.models import BillableItemType, InvoiceConfiguration
from NEMO_billing.models import CustomCharge, ProjectBillingHardCap
from NEMO_billing.tests.cap.test_cap_utilities import create_items
from NEMO_billing.tests.test_utilities import basic_data
from NEMO_billing.utilities import get_charges_amount_between


class TestProjectPrepayments(TestCase):
    def setUp(self) -> None:
        self.user, self.project, self.tool, self.area = basic_data(set_rate_category=True)
        self.project.projectbillingdetails.no_tax = True
        self.project.projectbillingdetails.save()
        self.project_hard_cap = ProjectBillingHardCap(project=self.project)
        self.assertRaises(ValidationError, self.project_hard_cap.full_clean)
        self.project_hard_cap.charge_types = str(BillableItemType.TOOL_USAGE.value)
        self.assertRaises(ValidationError, self.project_hard_cap.full_clean)
        self.project_hard_cap.amount = 30
        self.project_hard_cap.start_date = datetime.date.today()
        self.project_hard_cap.end_date = datetime.date.today()
        self.project_hard_cap.full_clean()
        self.project_hard_cap.save()
        self.tool, self.area, self.consumable, self.staff = create_items()

    def test_non_tax_exempt_configuration(self):
        self.project.projectbillingdetails.no_tax = False
        self.project.projectbillingdetails.save()
        self.assertRaises(ValidationError, self.project_hard_cap.full_clean)
        invoiceConfiguration = InvoiceConfiguration()
        invoiceConfiguration.name = "Config"
        invoiceConfiguration.email_from = "billing@test.com"
        invoiceConfiguration.merchant_name = "Atlantis Labs, LLC"
        invoiceConfiguration.tax = 10
        invoiceConfiguration.save()
        self.project_hard_cap.configuration = invoiceConfiguration
        self.project_hard_cap.full_clean()
        self.project_hard_cap.save()
        # the tool rate is 30 per hour, let's create an hour usage event
        start = timezone.now() - datetime.timedelta(hours=1)
        end = start + datetime.timedelta(hours=1)
        usage = UsageEvent.objects.create(
            user=self.user, operator=self.user, project=self.project, tool=self.tool, start=start, end=end
        )
        self.user.training_required = False
        self.user.save()
        self.user.qualifications.add(self.tool)
        # with taxes, it shouldn't be enough
        response = policy.check_to_enable_tool(
            self.tool, self.user, self.user, project=self.project, staff_charge=False
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertRaises(
            HardCAPReachedException, policy.check_billing_to_project, self.project, self.user, self.tool, usage
        )
        # 30 tool usage + 10% tax = 33
        start, end = get_month_timeframe(datetime.datetime.now().isoformat())
        self.assertEqual(get_charges_amount_between(self.project, invoiceConfiguration, start, end)[1], 33)
        # test with other dates, yesterday and tomorrow
        self.project_hard_cap.start_date = timezone.now() - timedelta(days=1)
        self.project_hard_cap.end_date = timezone.now() - timedelta(days=1)
        self.project_hard_cap.save()
        response = policy.check_to_enable_tool(
            self.tool, self.user, self.user, project=self.project, staff_charge=False
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.project_hard_cap.start_date = timezone.now() + timedelta(days=1)
        self.project_hard_cap.end_date = timezone.now() + timedelta(days=1)
        self.project_hard_cap.save()
        response = policy.check_to_enable_tool(
            self.tool, self.user, self.user, project=self.project, staff_charge=False
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_charge_types(self):
        start_charge = timezone.now() - datetime.timedelta(hours=1)
        end_charge = start_charge + datetime.timedelta(hours=1)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, project=self.project, tool=self.tool, start=start_charge, end=end_charge
        )
        start, end = get_month_timeframe(datetime.datetime.now().isoformat())
        self.assertEqual(get_charges_amount_between(self.project, None, start, end)[1], 30)
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TOOL_USAGE])[1],
            30,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.AREA_ACCESS])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.STAFF_CHARGE])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CUSTOM_CHARGE])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CONSUMABLE])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TRAINING])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.MISSED_RESERVATION])[1],
            0,
        )
        # Add area access record. Rate 40
        AreaAccessRecord.objects.create(
            area=self.area, customer=self.user, project=self.project, start=start_charge, end=end_charge
        )
        self.assertEqual(get_charges_amount_between(self.project, None, start, end)[1], 30 + 40)
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TOOL_USAGE])[1],
            30,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.AREA_ACCESS])[1],
            40,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.STAFF_CHARGE])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CUSTOM_CHARGE])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CONSUMABLE])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TRAINING])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.MISSED_RESERVATION])[1],
            0,
        )
        # Add ConsumableWithdraw 20 per item
        ConsumableWithdraw.objects.create(
            customer=self.user,
            project=self.project,
            consumable=self.consumable,
            quantity=1,
            date=end,
            merchant=self.staff,
        )
        self.assertEqual(get_charges_amount_between(self.project, None, start, end)[1], 30 + 40 + 20)
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TOOL_USAGE])[1],
            30,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.AREA_ACCESS])[1],
            40,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.STAFF_CHARGE])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CUSTOM_CHARGE])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CONSUMABLE])[1],
            20,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TRAINING])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.MISSED_RESERVATION])[1],
            0,
        )
        # Add Staff Charge 1h -> 25/hr
        StaffCharge.objects.create(
            staff_member=self.staff,
            customer=self.user,
            project=self.project,
            start=start_charge,
            end=end_charge,
        )
        self.assertEqual(get_charges_amount_between(self.project, None, start, end)[1], 30 + 40 + 20 + 25)
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TOOL_USAGE])[1],
            30,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.AREA_ACCESS])[1],
            40,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.STAFF_CHARGE])[1],
            25,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CUSTOM_CHARGE])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CONSUMABLE])[1],
            20,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TRAINING])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.MISSED_RESERVATION])[1],
            0,
        )
        # Add Custom Charge 5
        CustomCharge.objects.create(customer=self.user, project=self.project, date=end, amount=5, creator=self.staff)
        self.assertEqual(get_charges_amount_between(self.project, None, start, end)[1], 30 + 40 + 20 + 25 + 5)
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TOOL_USAGE])[1],
            30,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.AREA_ACCESS])[1],
            40,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.STAFF_CHARGE])[1],
            25,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CUSTOM_CHARGE])[1],
            5,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CONSUMABLE])[1],
            20,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TRAINING])[1],
            0,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.MISSED_RESERVATION])[1],
            0,
        )
        # Add training -> rate 10
        TrainingSession.objects.create(
            trainee=self.user,
            project=self.project,
            date=end,
            trainer=self.staff,
            duration=60,
            tool=self.tool,
            type=TrainingSession.Type.INDIVIDUAL,
        )
        self.assertEqual(get_charges_amount_between(self.project, None, start, end)[1], 30 + 40 + 20 + 25 + 5 + 10)
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TOOL_USAGE])[1],
            30,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.AREA_ACCESS])[1],
            40,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.STAFF_CHARGE])[1],
            25,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CUSTOM_CHARGE])[1],
            5,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CONSUMABLE])[1],
            20,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TRAINING])[1],
            10,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.MISSED_RESERVATION])[1],
            0,
        )
        # Add missed reservation -> rate 15
        Reservation.objects.create(
            user=self.user,
            creator=self.user,
            project=self.project,
            start=start_charge,
            end=end_charge,
            missed=True,
            tool=self.tool,
            short_notice=False,
        )
        self.assertEqual(get_charges_amount_between(self.project, None, start, end)[1], 30 + 40 + 20 + 25 + 5 + 10 + 15)
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TOOL_USAGE])[1],
            30,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.AREA_ACCESS])[1],
            40,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.STAFF_CHARGE])[1],
            25,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CUSTOM_CHARGE])[1],
            5,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.CONSUMABLE])[1],
            20,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.TRAINING])[1],
            10,
        )
        self.assertEqual(
            get_charges_amount_between(self.project, None, start, end, [BillableItemType.MISSED_RESERVATION])[1],
            15,
        )
