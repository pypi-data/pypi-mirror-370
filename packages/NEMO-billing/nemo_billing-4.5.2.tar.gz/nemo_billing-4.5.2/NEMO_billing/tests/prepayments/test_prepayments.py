import datetime
from http import HTTPStatus
from typing import List, Optional

from NEMO.models import Account, EmailLog, UsageEvent, User
from NEMO.policy import policy_class as policy
from NEMO.utilities import get_month_timeframe
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from NEMO_billing.customization import BillingCustomization
from NEMO_billing.exceptions import ChargeTypeNotAllowedForProjectException
from NEMO_billing.invoices.models import BillableItemType, Invoice, InvoiceConfiguration
from NEMO_billing.invoices.processors import invoice_data_processor_class as processor
from NEMO_billing.prepayments.exceptions import (
    ProjectFundsExpiredException,
    ProjectFundsInactiveException,
    ProjectFundsNotSetException,
    ProjectInsufficientFundsException,
)
from NEMO_billing.prepayments.models import Fund, FundType, ProjectPrepaymentDetail
from NEMO_billing.tests.cap.test_cap_utilities import add_charges_of_type, create_items, get_other_billable_types
from NEMO_billing.tests.test_utilities import basic_data
from NEMO_billing.utilities import get_charges_amount_between, number_of_months_between_dates


class TestProjectPrepayments(TestCase):
    def setUp(self) -> None:
        self.user, self.project, self.tool, self.area = basic_data(set_rate_category=True)
        self.project.projectbillingdetails.no_tax = True
        self.project.projectbillingdetails.save()
        self.project_prepayment = ProjectPrepaymentDetail(project=self.project)
        self.assertRaises(ValidationError, self.project_prepayment.full_clean)
        self.project_prepayment.charge_types = str(BillableItemType.TOOL_USAGE.value)
        self.project_prepayment.full_clean()
        self.project_prepayment.save()
        self.fund_type = FundType.objects.create(name="Credit", display_order=1)
        self.fund_type.save()
        self.tool, self.area, self.consumable, self.staff = create_items()

    def test_prepayment(self):
        # No funds set
        self.assertRaises(
            ProjectFundsNotSetException, policy.check_billing_to_project, self.project, self.user, self.tool
        )
        new_fund = Fund()
        new_fund.project_prepayment = self.project_prepayment
        new_fund.amount = 30
        # No fund type
        self.assertRaises(ValidationError, new_fund.full_clean)
        new_fund.fund_type = self.fund_type
        # No start date
        self.assertRaises(ValidationError, new_fund.full_clean)
        new_fund.start_date = datetime.date.today()
        new_fund.save()
        self.assertEqual(new_fund.balance, new_fund.amount)
        # No active funds (start next month)
        new_fund.start_date = datetime.date.today() + relativedelta(months=1)
        new_fund.save()
        self.assertRaises(
            ProjectFundsInactiveException, policy.check_billing_to_project, self.project, self.user, self.tool
        )
        second_fund = Fund()
        second_fund.fund_type = self.fund_type
        second_fund.project_prepayment = self.project_prepayment
        second_fund.amount = 10
        second_fund.start_date = datetime.date.today()
        second_fund.save()
        # At least one good fund, all good
        policy.check_billing_to_project(self.project, self.user, self.tool)
        second_fund.delete()
        # Expired funds
        new_fund.start_date = datetime.date.today()
        new_fund.expiration_date = datetime.date.today()
        new_fund.save()
        self.assertRaises(
            ProjectFundsExpiredException, policy.check_billing_to_project, self.project, self.user, self.tool
        )
        second_fund.save()
        # Second fund doesn't expire, all good
        policy.check_billing_to_project(self.project, self.user, self.tool)
        second_fund.delete()
        new_fund.expiration_date = datetime.date.today() + relativedelta(months=1)
        new_fund.save()
        # the tool rate is 30 per hour, let's create an hour usage event
        start = timezone.now() - datetime.timedelta(hours=1)
        end = start + datetime.timedelta(hours=1)
        # Project billing is good
        policy.check_billing_to_project(self.project, self.user, self.tool)
        # Enable usage is good
        self.user.qualifications.add(self.tool)
        self.user.training_required = False
        self.user.save()
        r = policy.check_to_enable_tool(self.tool, self.user, self.user, project=self.project, staff_charge=False)
        self.assertEqual(r.status_code, HTTPStatus.OK)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, project=self.project, tool=self.tool, start=start, end=end
        )
        # If tool usage is not enabled
        self.project_prepayment.charge_types = str(BillableItemType.AREA_ACCESS.value)
        self.project_prepayment.save()
        r = policy.check_to_enable_tool(self.tool, self.user, self.user, project=self.project, staff_charge=False)
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        # Put it back
        self.project_prepayment.charge_types = str(BillableItemType.TOOL_USAGE.value)
        self.project_prepayment.save()
        # We should now have an error with insufficient funds
        # Project billing should not be
        r = policy.check_to_enable_tool(self.tool, self.user, self.user, project=self.project, staff_charge=False)
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertRaises(
            ProjectInsufficientFundsException, policy.check_billing_to_project, self.project, self.user, self.tool
        )
        # Set fund balance a bit lower
        new_fund.balance = 15
        new_fund.save()
        # Set overdraft and check it will allow it
        self.project_prepayment.overdraft_amount_allowed = 20
        self.project_prepayment.save()
        r = policy.check_to_enable_tool(self.tool, self.user, self.user, project=self.project, staff_charge=False)
        self.assertEqual(r.status_code, HTTPStatus.OK)
        policy.check_billing_to_project(self.project, self.user, self.tool)
        # Overdraft not sufficient
        self.project_prepayment.overdraft_amount_allowed = 10
        self.project_prepayment.save()
        r = policy.check_to_enable_tool(self.tool, self.user, self.user, project=self.project, staff_charge=False)
        self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)
        self.assertRaises(
            ProjectInsufficientFundsException, policy.check_billing_to_project, self.project, self.user, self.tool
        )
        # Remove overdraft, restore fund balance
        new_fund.balance = 30
        new_fund.save()
        self.project_prepayment.overdraft_amount_allowed = None
        self.project_prepayment.save()
        # Add additional funds
        second_fund.save()
        # All good now
        policy.check_billing_to_project(self.project, self.user, self.tool)
        # Change first fund and make sure we are still good
        new_fund.amount = 25
        new_fund.balance = 25
        new_fund.save()
        # Set low balance and also check that email was sent
        self.assertEqual(EmailLog.objects.count(), 0)
        second_fund.balance_warning_percent = 50
        second_fund.save()
        BillingCustomization.set("billing_accounting_email_address", "accounting@example.com")
        r = policy.check_to_enable_tool(self.tool, self.user, self.user, project=self.project, staff_charge=False)
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertEqual(EmailLog.objects.count(), 1)
        self.assertTrue("Low fund balance for project" in EmailLog.objects.first().subject)
        # Do it again it should not be sent (only once)
        r = policy.check_to_enable_tool(self.tool, self.user, self.user, project=self.project, staff_charge=False)
        self.assertEqual(r.status_code, HTTPStatus.OK)
        # Still one email
        self.assertEqual(EmailLog.objects.count(), 1)
        self.assertTrue("Low fund balance for project" in EmailLog.objects.first().subject)
        # Generate invoice and check new fund balances
        self.generate_invoice(timezone.now())
        self.assertEqual(Fund.objects.get(id=new_fund.id).balance, 0)
        self.assertEqual(Fund.objects.get(id=second_fund.id).balance, 5)

    def test_all_types_of_charges(self):
        # Test each charge
        for billable_type in BillableItemType:
            with self.subTest(billable_type.name):
                self.charges_subtest([billable_type])
        # Test combination of charges
        for i in range(1, 8):
            for j in range(i + 1, 8):
                with self.subTest(f"{BillableItemType(i).name}-{BillableItemType(j).name}"):
                    self.charges_subtest([BillableItemType(i), BillableItemType(j)])

    def charges_subtest(self, billable_charge_types: List[BillableItemType]):
        project_prepayment = self.project_prepayment
        project_prepayment.charge_types = ",".join([str(t.value) for t in billable_charge_types])
        project_prepayment.full_clean()
        project_prepayment.save()
        add_charges_of_type(self, project_prepayment.billable_charge_types, timezone.now())
        self.assertRaises(
            ChargeTypeNotAllowedForProjectException,
            add_charges_of_type,
            self,
            get_other_billable_types(project_prepayment.billable_charge_types),
            timezone.now(),
        )

    def test_non_tax_exempt_configuration(self):
        self.project.projectbillingdetails.no_tax = False
        self.project.projectbillingdetails.save()
        self.assertRaises(ValidationError, self.project_prepayment.full_clean)
        invoiceConfiguration = InvoiceConfiguration()
        invoiceConfiguration.name = "Config"
        invoiceConfiguration.email_from = "billing@test.com"
        invoiceConfiguration.merchant_name = "Atlantis Labs, LLC"
        invoiceConfiguration.tax = 10
        invoiceConfiguration.save()
        self.project_prepayment.configuration = invoiceConfiguration
        self.project_prepayment.full_clean()
        self.project_prepayment.save()
        # the tool rate is 30 per hour, let's create an hour usage event
        start = timezone.now() - datetime.timedelta(hours=1)
        end = start + datetime.timedelta(hours=1)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, project=self.project, tool=self.tool, start=start, end=end
        )
        # Let's say we have enough funds to cover, like 31
        new_fund = Fund()
        new_fund.fund_type = self.fund_type
        new_fund.project_prepayment = self.project_prepayment
        new_fund.amount = 31
        new_fund.start_date = datetime.date.today()
        new_fund.save()
        self.user.training_required = False
        self.user.save()
        self.user.qualifications.add(self.tool)
        # with taxes, it shouldn't be enough
        response = policy.check_to_enable_tool(
            self.tool, self.user, self.user, project=self.project, staff_charge=False
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertRaises(
            ProjectInsufficientFundsException, policy.check_billing_to_project, self.project, self.user, self.tool
        )
        # 30 tool usage + 10% tax = 33
        start, end = get_month_timeframe(datetime.datetime.now().isoformat())
        self.assertEqual(get_charges_amount_between(self.project, invoiceConfiguration, start, end)[1], 33)

    def test_month_diff(self):
        self.assertEqual(
            number_of_months_between_dates(datetime.datetime(2010, 1, 1), datetime.datetime(2010, 1, 1)), 0
        )
        self.assertEqual(
            number_of_months_between_dates(datetime.datetime(2010, 1, 1), datetime.datetime(2009, 12, 1)), 1
        )
        self.assertEqual(
            number_of_months_between_dates(datetime.datetime(2010, 10, 1), datetime.datetime(2010, 9, 1)), 1
        )
        self.assertEqual(
            number_of_months_between_dates(datetime.datetime(2010, 10, 1), datetime.datetime(2009, 10, 1)), 12
        )
        self.assertEqual(
            number_of_months_between_dates(datetime.datetime(2010, 10, 1), datetime.datetime(2009, 11, 1)), 11
        )
        self.assertEqual(
            number_of_months_between_dates(datetime.datetime(2010, 10, 1), datetime.datetime(2009, 8, 1)), 14
        )

    def test_span_month(self):
        # Check that charges in different month with funds being active late or expiring still works
        pass

    def test_low_balance_email(self):
        # Check not sent if more funds are active
        # Check only sent once per fund
        # Check only sent if warning threshold set
        # Check sent to last fund if multiple active ones
        self.user.is_accounting_officer = True
        self.user.save()
        new_fund = Fund()
        new_fund.project_prepayment = self.project_prepayment
        new_fund.amount = 25
        new_fund.balance_warning_percent = 50
        new_fund.fund_type = self.fund_type
        new_fund.start_date = datetime.date.today()
        new_fund.save()
        self.assertFalse(EmailLog.objects.exists())
        new_fund.check_for_low_balance(20, True)
        self.assertFalse(EmailLog.objects.exists())
        new_fund.check_for_low_balance(10, True)
        self.assertFalse(EmailLog.objects.exists())

    def test_void_invoice(self):
        new_fund = Fund()
        new_fund.project_prepayment = self.project_prepayment
        new_fund.amount = 25
        new_fund.fund_type = self.fund_type
        new_fund.start_date = datetime.date.today()
        new_fund.save()
        self.assertEqual(new_fund.balance, new_fund.amount)
        second_fund = Fund()
        second_fund.fund_type = self.fund_type
        second_fund.project_prepayment = self.project_prepayment
        second_fund.amount = 10
        second_fund.start_date = datetime.date.today()
        second_fund.save()
        # the tool rate is 30 per hour, let's create an hour usage event
        start = timezone.now() - datetime.timedelta(hours=1)
        end = start + datetime.timedelta(hours=1)
        # Project billing is good
        policy.check_billing_to_project(self.project, self.user, self.tool)
        # Enable usage is good
        self.user.qualifications.add(self.tool)
        self.user.training_required = False
        self.user.save()
        response = policy.check_to_enable_tool(
            self.tool, self.user, self.user, project=self.project, staff_charge=False
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, project=self.project, tool=self.tool, start=start, end=end
        )
        invoice = self.generate_invoice(timezone.now())[0]
        self.assertEqual(Fund.objects.get(id=new_fund.id).balance, 0)
        self.assertEqual(Fund.objects.get(id=second_fund.id).balance, 5)
        # Now void the invoice and the amounts should be put back
        accounting = User.objects.create(
            first_name="Staffy", last_name="McStaffer", username="staffy", is_accounting_officer=True
        )
        self.client.force_login(accounting)
        self.client.post(reverse("void_invoice", args=[invoice.id]), follow=True)
        self.assertEqual(Fund.objects.get(id=new_fund.id).balance, 25)
        self.assertEqual(Fund.objects.get(id=second_fund.id).balance, 10)

    def generate_invoice(self, invoice_date, account: Account = None) -> Optional[List[Invoice]]:
        invoice_configuration = InvoiceConfiguration.first_or_default()
        if not invoice_configuration.id:
            invoice_configuration.save()
        month = invoice_date.strftime("%B %Y")
        account = account or self.project.account
        return processor.generate_invoice_for_account(month, account, invoice_configuration, self.user)
