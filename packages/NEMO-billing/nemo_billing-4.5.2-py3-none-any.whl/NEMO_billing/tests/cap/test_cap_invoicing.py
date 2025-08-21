from _decimal import Decimal
from datetime import date, timedelta
from typing import List, Optional

from NEMO.models import Account, Project, UsageEvent, User
from NEMO.utilities import RecurrenceFrequency, new_model_copy
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from NEMO_billing.admin import save_or_delete_core_facility
from NEMO_billing.cap_discount.customization import CAPDiscountCustomization
from NEMO_billing.cap_discount.exceptions import MissingCAPAmountException
from NEMO_billing.cap_discount.models import CAPDiscount, CAPDiscountAmount, CAPDiscountConfiguration, CAPDiscountTier
from NEMO_billing.cap_discount.processors import AccountDiscountCalculator
from NEMO_billing.invoices.models import BillableItemType, Invoice, InvoiceConfiguration, ProjectBillingDetails
from NEMO_billing.invoices.processors import invoice_data_processor_class as processor
from NEMO_billing.models import CoreFacility
from NEMO_billing.rates.models import Rate, RateCategory, RateType
from NEMO_billing.tests.cap.test_cap_utilities import add_charges_of_type, create_items
from NEMO_billing.tests.test_utilities import basic_data


class TestCapInvoicing(TestCase):
    def setUp(self) -> None:
        self.modify_settings(INSTALLED_APPS={"prepend": "NEMO_billing.cap_discount"})
        self.user, self.project, self.tool, self.area = basic_data(set_rate_category=True)
        cap_configuration = CAPDiscountConfiguration(rate_category=self.project.projectbillingdetails.category)
        # Yearly cap
        cap_configuration.reset_frequency = RecurrenceFrequency.YEARLY.value
        # Started 10 month ago
        cap_configuration.start = date.today() - relativedelta(months=10)
        cap_configuration.start_on_first_charge = False
        # Only for tool usage
        cap_configuration.charge_types = BillableItemType.TOOL_USAGE.value
        cap_configuration.save()
        # 25% discount
        CAPDiscountTier.objects.create(
            cap_discount_configuration=cap_configuration, amount=Decimal("100"), discount=Decimal("25")
        )
        self.cap_configuration: CAPDiscountConfiguration = CAPDiscountConfiguration.objects.get(pk=cap_configuration.pk)
        self.tool, self.area, self.consumable, self.staff = create_items()

    def test_invoice_different_account_cap(self):
        # let's create a new account and generate invoice. nothing should change
        self.cap_configuration.start = None
        self.cap_configuration.save()
        new_project = Project.objects.create(name="new proj", account=Account.objects.create(name="new_acc"))
        new_project.projectbillingdetails = ProjectBillingDetails.objects.create(project=new_project)
        last_month_date = timezone.now() - relativedelta(months=1)
        add_charges_of_type(self, [BillableItemType.TOOL_USAGE], last_month_date)
        self.generate_invoice(last_month_date, new_project.account)
        self.assertFalse(CAPDiscountAmount.objects.filter(cap_discount__account=new_project.account).exists())
        self.assertFalse(CAPDiscountAmount.objects.filter(cap_discount__account=self.project.account).exists())

    def test_invoice_missing_amount_cap_error(self):
        # Let's set some charges 4 months ago, the start date is already set at 10 month ago
        four_month_ago_date = timezone.now() - relativedelta(months=4)
        add_charges_of_type(self, [BillableItemType.TOOL_USAGE], four_month_ago_date)
        # Run an invoice now, that's fine, even if the start date was before
        one_month_ago_date = timezone.now() - relativedelta(months=1)
        invoice = self.generate_invoice(one_month_ago_date)
        # No recent charges, so no invoice
        self.assertFalse(invoice)
        # Delete CAP discount so we can try again
        CAPDiscount.objects.all().delete()
        # Generate invoice 4 months ago
        self.generate_invoice(four_month_ago_date)
        # Try now, this should fail because we are missing invoices for the past 2 months ago
        self.assertRaises(MissingCAPAmountException, self.generate_invoice, one_month_ago_date)
        # Try 2 months ago, same
        two_month_ago_date = timezone.now() - relativedelta(months=2)
        self.assertRaises(MissingCAPAmountException, self.generate_invoice, two_month_ago_date)
        # Try 3 months ago, this time it should work
        three_month_ago_date = timezone.now() - relativedelta(months=3)
        self.generate_invoice(three_month_ago_date)
        # Now we can generate the other ones up to today
        self.generate_invoice(two_month_ago_date)
        self.generate_invoice(one_month_ago_date)

    def test_invoice_missing_amount_cap_error_auto_start(self):
        # Try with start date empty.
        self.cap_configuration.start = None
        self.cap_configuration.start_on_first_charge = True
        self.cap_configuration.save()
        self.test_invoice_missing_amount_cap_error()

    def test_new_month_start(self):
        # Let's set some charges 3 months ago, as well as the start date.
        three_month_ago_date = timezone.now() - relativedelta(months=3)
        self.cap_configuration.start = three_month_ago_date
        self.cap_configuration.save()
        add_charges_of_type(self, [BillableItemType.TOOL_USAGE], three_month_ago_date)
        self.generate_invoice(three_month_ago_date, account=self.project.account)
        # Rate is 30 per hour, the previous function added 24 hours usage
        charge = 30 * 24
        cap_amount = CAPDiscountAmount.objects.get(
            cap_discount__configuration=self.cap_configuration,
            cap_discount__account=self.project.account,
            month=three_month_ago_date.month,
            year=three_month_ago_date.year,
        )
        self.assertEqual(cap_amount.end, charge)
        # new month should start with last month's end amount, and end with + new charges
        two_month_ago_date = timezone.now() - relativedelta(months=2)
        add_charges_of_type(self, [BillableItemType.TOOL_USAGE], two_month_ago_date)
        # Add new charge under the same user/account but different project
        tool_end = two_month_ago_date
        tool_start = tool_end - timedelta(hours=2)
        new_tool_charge = 30 * 2
        new_project = Project.objects.create(name="new proj", account=self.project.account)
        category = RateCategory.objects.get(name="Academia")
        new_project.projectbillingdetails = ProjectBillingDetails.objects.create(project=new_project, category=category)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=new_project, start=tool_start, end=tool_end
        )
        self.generate_invoice(two_month_ago_date, account=self.project.account)
        new_cap_amount = CAPDiscountAmount.objects.get(
            cap_discount__configuration=self.cap_configuration,
            cap_discount__account=self.project.account,
            month=two_month_ago_date.month,
            year=two_month_ago_date.year,
        )
        self.assertEqual(new_cap_amount.start, cap_amount.end)
        self.assertEqual(new_cap_amount.end, cap_amount.end + new_tool_charge + charge)

    def test_month_start_different_facility(self):
        # We already have a cap with no facility, let's create another one with a facility. It should have a start amount after generating invoice
        self.cap_configuration.start = date.today()
        self.cap_configuration.save()
        facility = CoreFacility.objects.create(name="facility")
        new_cap_configuration = new_model_copy(self.cap_configuration)
        new_cap_configuration.save()
        new_cap_configuration.core_facilities.set([facility])
        save_or_delete_core_facility(self.tool, facility, "tool")
        add_charges_of_type(self, [BillableItemType.TOOL_USAGE], timezone.now())
        # Rate is 30 per hour, the previous function added 24 hours usage
        charge = 30 * 24
        self.generate_invoice(timezone.now().astimezone(), account=self.project.account)
        cap_amount = CAPDiscountAmount.objects.filter(cap_discount__configuration=self.cap_configuration).first()
        new_cap_amount = CAPDiscountAmount.objects.filter(cap_discount__configuration=new_cap_configuration).first()
        self.assertTrue(new_cap_amount)
        self.assertEqual(new_cap_amount.start, 0)
        self.assertEqual(new_cap_amount.end, charge)
        # New cap is set for different core facility
        self.assertFalse(cap_amount)

    def test_month_start_different_user(self):
        self.cap_configuration.start = date.today()
        self.cap_configuration.save()
        # Charges added are for the user, so they should not be added to staff's CAP
        add_charges_of_type(self, [BillableItemType.TOOL_USAGE], timezone.now())
        self.generate_invoice(timezone.now().astimezone(), account=self.project.account)
        cap_amount = CAPDiscountAmount.objects.filter(cap_discount__user=self.user).first()
        cap_staff_amount = CAPDiscountAmount.objects.filter(cap_discount__user=self.staff).first()
        self.assertTrue(cap_amount)
        self.assertEqual(cap_amount.start, 0)
        self.assertEqual(cap_amount.end, 24 * 30)
        self.assertFalse(cap_staff_amount)

    def test_excluded_tool(self):
        self.cap_configuration.start = date.today()
        self.cap_configuration.save()
        # Add a tool charge
        add_charges_of_type(self, [BillableItemType.TOOL_USAGE], timezone.now())
        invoice = self.generate_invoice(timezone.now().astimezone(), account=self.project.account)[0]
        cap_amount = CAPDiscountAmount.objects.filter(cap_discount__configuration=self.cap_configuration).first()
        charge = 30 * 24
        discount = (charge - self.cap_configuration.capdiscounttier_set.first().amount) * Decimal(0.25)
        # Everything set correctly
        self.assertTrue(cap_amount)
        self.assertEqual(cap_amount.start, 0)
        self.assertEqual(cap_amount.end, charge)
        self.assertEqual(invoice.total_amount, charge - discount)
        # Now reset and exclude the tool
        invoice.delete()
        CAPDiscount.objects.all().delete()
        CAPDiscountCustomization.set("cap_billing_exclude_tools", f"{self.tool.id}")
        invoice = self.generate_invoice(timezone.now().astimezone(), account=self.project.account)[0]
        cap_amount = CAPDiscountAmount.objects.filter(cap_discount__configuration=self.cap_configuration).first()
        # CAP amount doesn't exist, but invoice stayed unchanged
        self.assertFalse(cap_amount)
        self.assertEqual(invoice.total_amount, charge)

    def test_new_month_reset(self):
        # Let's set some charges and set cap renewal to 2 months
        today_datetime = timezone.now().astimezone()
        two_month_ago_date = today_datetime - relativedelta(months=2)
        self.cap_configuration.start = two_month_ago_date.date()
        self.cap_configuration.reset_interval = 2
        self.cap_configuration.reset_frequency = RecurrenceFrequency.MONTHLY.value
        self.cap_configuration.save()
        add_charges_of_type(self, [BillableItemType.TOOL_USAGE], two_month_ago_date)
        self.generate_invoice(two_month_ago_date, account=self.project.account)
        # try last month
        last_month = today_datetime - relativedelta(months=1)
        self.generate_invoice(last_month, account=self.project.account)
        # Rate is 30 per hour, the previous function added 24 hours usage
        charge = 30 * 24
        cap_amount = CAPDiscountAmount.objects.get(
            cap_discount__configuration=self.cap_configuration, month=last_month.month, year=last_month.year
        )
        # Should have start and end amount be the same since we have no new charges
        self.assertEqual(cap_amount.end, charge)
        self.assertEqual(cap_amount.start, charge)
        # Now generate new invoice. cap should reset
        self.generate_invoice(today_datetime, account=self.project.account)
        cap_amount = CAPDiscountAmount.objects.get(
            cap_discount__configuration=self.cap_configuration, month=today_datetime.month, year=today_datetime.year
        )
        self.assertEqual(cap_amount.start, 0)
        self.assertEqual(cap_amount.end, 0)

    def test_rollback_if_one_project_invoice_has_error(self):
        pass

    def test_discount_invoice_same_project(self):
        # Our cap is at 100, and discount 25%. Set start 2 month ago
        two_month_ago_date = timezone.now() - relativedelta(months=2)
        self.cap_configuration.start = two_month_ago_date
        self.cap_configuration.save()
        # Add charges 2 months ago, make sure the end is earlier, so it counts for cap before the others
        end = two_month_ago_date - timedelta(minutes=20)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=self.project, start=start, end=end
        )
        # 30 per hour for 2 hours
        charge_1 = 30 * 2
        last_invoice: Invoice = self.generate_invoice(two_month_ago_date, self.project.account)[0]
        self.assertEqual(last_invoice.total_amount, charge_1)
        # Reset
        last_invoice.delete()
        CAPDiscount.objects.all().delete()
        # Add new charge for one hour, still no discount
        end = two_month_ago_date - timedelta(minutes=15)
        start = end - timedelta(hours=1)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=self.project, start=start, end=end
        )
        charge_2 = 30 * 1
        last_invoice: Invoice = self.generate_invoice(two_month_ago_date, self.project.account)[0]
        self.assertEqual(last_invoice.total_amount, charge_1 + charge_2)
        # Add new charge for one hour, this time it should be discounted 25% on the difference
        last_invoice.delete()
        CAPDiscount.objects.all().delete()
        end = two_month_ago_date - timedelta(minutes=10)
        start = end - timedelta(hours=1)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=self.project, start=start, end=end
        )
        # 25% discount
        charge_3 = 30 * 1 - (20 * 0.25)
        last_invoice: Invoice = self.generate_invoice(two_month_ago_date, self.project.account)[0]
        self.assertEqual(last_invoice.total_amount, charge_1 + charge_2 + charge_3)
        # Add new charges to different project, but under the same account. It should count towards CAP
        # And the second project should have the discount as well
        last_invoice.delete()
        CAPDiscount.objects.all().delete()
        new_project = Project.objects.create(name="new proj", account=self.project.account)
        category = RateCategory.objects.get(name="Academia")
        new_project.projectbillingdetails = ProjectBillingDetails.objects.create(project=new_project, category=category)
        end = two_month_ago_date - timedelta(minutes=5)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=new_project, start=start, end=end
        )
        charge_4 = 30 * 2 - (30 * 2 * 0.25)
        invoices = self.generate_invoice(two_month_ago_date, self.project.account)
        self.assertEqual(len(invoices), 2)
        project_invoice: Invoice = [invoice for invoice in invoices if invoice.project_details.project == self.project][
            0
        ]
        self.assertEqual(project_invoice.total_amount, charge_1 + charge_2 + charge_3)
        new_project_invoice: Invoice = [
            invoice for invoice in invoices if invoice.project_details.project == new_project
        ][0]
        self.assertEqual(new_project_invoice.total_amount, charge_4)

    def test_discount_invoice_no_users(self):
        # Set configuration to NOT split by users
        self.cap_configuration.split_by_user = False
        # Our cap is at 100, and discount 25%. Set start 2 month ago
        two_month_ago_date = timezone.now() - relativedelta(months=2)
        self.cap_configuration.start = two_month_ago_date
        self.cap_configuration.save()
        # Add charges 2 months ago, make sure the end is earlier, so it counts for cap before the others
        end = two_month_ago_date - timedelta(minutes=20)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=self.project, start=start, end=end
        )
        # 30 per hour for 3 hours
        charge_1 = 30 * 2
        last_invoice: Invoice = self.generate_invoice(two_month_ago_date, self.project.account)[0]
        self.assertEqual(last_invoice.total_amount, charge_1)
        # Reset
        last_invoice.delete()
        CAPDiscount.objects.all().delete()
        # Add new charge for one hour, still no discount
        end = two_month_ago_date - timedelta(minutes=15)
        start = end - timedelta(hours=1)
        UsageEvent.objects.create(
            user=self.staff, operator=self.staff, tool=self.tool, project=self.project, start=start, end=end
        )
        charge_2 = 30 * 1
        last_invoice: Invoice = self.generate_invoice(two_month_ago_date, self.project.account)[0]
        self.assertEqual(last_invoice.total_amount, charge_1 + charge_2)
        # Add new charge for one hour, this time it should be discounted 25% on the difference
        last_invoice.delete()
        CAPDiscount.objects.all().delete()
        end = two_month_ago_date - timedelta(minutes=10)
        start = end - timedelta(hours=1)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=self.project, start=start, end=end
        )
        # 25% discount on 20 of the $30 charge (reached 100)
        charge_3 = 30 * 1 - (20 * 0.25)
        last_invoice: Invoice = self.generate_invoice(two_month_ago_date, self.project.account)[0]
        self.assertEqual(last_invoice.total_amount, charge_1 + charge_2 + charge_3)
        # Add new charges to different project, but under the same account. It should count towards CAP
        # And the second project should have the discount as well
        last_invoice.delete()
        CAPDiscount.objects.all().delete()
        new_project = Project.objects.create(name="new proj", account=self.project.account)
        category = RateCategory.objects.get(name="Academia")
        new_project.projectbillingdetails = ProjectBillingDetails.objects.create(project=new_project, category=category)
        end = two_month_ago_date - timedelta(minutes=5)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=new_project, start=start, end=end
        )
        charge_4 = 30 * 2 - (30 * 2 * 0.25)
        invoices = self.generate_invoice(two_month_ago_date, self.project.account)
        self.assertEqual(len(invoices), 2)
        project_invoice: Invoice = [invoice for invoice in invoices if invoice.project_details.project == self.project][
            0
        ]
        self.assertEqual(project_invoice.total_amount, charge_1 + charge_2 + charge_3)
        new_project_invoice: Invoice = [
            invoice for invoice in invoices if invoice.project_details.project == new_project
        ][0]
        self.assertEqual(new_project_invoice.total_amount, charge_4)
        # Add new discount tier > 140 => 50%
        self.cap_configuration.capdiscounttier_set.add(
            CAPDiscountTier.objects.create(cap_discount_configuration=self.cap_configuration, amount=140, discount=50)
        )
        for invoice in invoices:
            invoice.delete()
        CAPDiscount.objects.all().delete()
        invoices = self.generate_invoice(two_month_ago_date, self.project.account)
        self.assertEqual(len(invoices), 2)
        project_invoice: Invoice = [invoice for invoice in invoices if invoice.project_details.project == self.project][
            0
        ]
        # charges 1-3 are unchanged (total of 120 < 140)
        self.assertEqual(project_invoice.total_amount, charge_1 + charge_2 + charge_3)
        new_project_invoice: Invoice = [
            invoice for invoice in invoices if invoice.project_details.project == new_project
        ][0]
        # charge 4 is now split, 20 to reach 140 at 25%, then the remaining 40 at 50% discount
        charge_4 = 30 * 2 - (20 * 0.25) - (40 * 0.5)
        self.assertEqual(new_project_invoice.total_amount, charge_4)

    def test_void_related_invoices(self):
        accounting = User.objects.create(
            first_name="Staffy", last_name="McStaffer", username="staffy", is_accounting_officer=True
        )
        # Our cap is at 100, and discount 25%. Set start 3 month ago
        three_month_ago_date = timezone.now() - relativedelta(months=3)
        two_month_ago_date = timezone.now() - relativedelta(months=2)
        self.cap_configuration.start = three_month_ago_date
        self.cap_configuration.save()
        # Add charges 3 months ago
        end = three_month_ago_date - timedelta(minutes=20)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=self.project, start=start, end=end
        )
        # Add charges 2 months ago
        end = two_month_ago_date - timedelta(minutes=20)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=self.project, start=start, end=end
        )
        # Add new charges to different project, but under the same account.
        new_project = Project.objects.create(name="new proj", account=self.project.account)
        category = RateCategory.objects.get(name="Academia")
        new_project.projectbillingdetails = ProjectBillingDetails.objects.create(project=new_project, category=category)
        end = two_month_ago_date - timedelta(minutes=5)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=new_project, start=start, end=end
        )
        # Generate invoices 3 months ago, then 2 months ago
        first_invoices = self.generate_invoice(three_month_ago_date, self.project.account)
        invoices = self.generate_invoice(two_month_ago_date, self.project.account)
        self.assertEqual(len(invoices), 2)
        self.client.force_login(accounting)
        # Void one of the earliest invoices, should fail
        response = self.client.post(reverse("void_invoice", args=[first_invoices[0].id]), follow=True)
        self.assertContains(
            response, "You can only void/delete the latest invoices when a CAP is associated with it", status_code=200
        )
        # Void one of the latest invoices, the other one should also be voided and the amounts should be deleted as well
        self.client.post(reverse("void_invoice", args=[invoices[0].id]), follow=True)
        self.assertTrue(
            all(
                [
                    invoice.voided_date and invoice.voided_by == accounting
                    for invoice in Invoice.objects.filter(id__in=[invoice.id for invoice in invoices])
                ]
            )
        )
        self.assertFalse(
            CAPDiscountAmount.objects.filter(
                cap_discount__account=self.project.account, year=two_month_ago_date.year, month=two_month_ago_date.month
            ).exists()
        )
        # CAP discount should still exist
        self.assertTrue(CAPDiscount.objects.filter(account=self.project.account).exists())
        # Now void previous one, we have nothing left
        self.client.post(reverse("void_invoice", args=[first_invoices[0].id]), follow=True)
        self.assertTrue(Invoice.objects.get(pk=first_invoices[0].id).voided_date)
        self.assertFalse(CAPDiscountAmount.objects.all().exists())
        self.assertFalse(CAPDiscount.objects.all().exists())

    def test_delete_related_invoices(self):
        accounting = User.objects.create(
            first_name="Staffy", last_name="McStaffer", username="staffy", is_accounting_officer=True
        )
        # Our cap is at 100, and discount 25%. Set start 3 month ago
        three_month_ago_date = timezone.now() - relativedelta(months=3)
        two_month_ago_date = timezone.now() - relativedelta(months=2)
        self.cap_configuration.start = three_month_ago_date
        self.cap_configuration.save()
        # Add charges 3 months ago
        end = three_month_ago_date - timedelta(minutes=20)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=self.project, start=start, end=end
        )
        # Add charges 2 months ago
        end = two_month_ago_date - timedelta(minutes=20)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=self.project, start=start, end=end
        )
        # Add new charges to different project, but under the same account.
        new_project = Project.objects.create(name="new proj", account=self.project.account)
        category = RateCategory.objects.get(name="Academia")
        new_project.projectbillingdetails = ProjectBillingDetails.objects.create(project=new_project, category=category)
        end = two_month_ago_date - timedelta(minutes=5)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=new_project, start=start, end=end
        )
        # Generate invoices 3 months ago, then 2 months ago
        first_invoices = self.generate_invoice(three_month_ago_date, self.project.account)
        invoices = self.generate_invoice(two_month_ago_date, self.project.account)
        self.assertEqual(len(invoices), 2)
        self.client.force_login(accounting)
        # Delete one of the earliest invoices, should fail
        response = self.client.post(reverse("delete_invoice", args=[first_invoices[0].id]), follow=True)
        self.assertContains(
            response, "You can only void/delete the latest invoices when a CAP is associated with it", status_code=200
        )
        # Delete one of the latest invoices, the other one should also be deleted and the amounts should be deleted as well
        self.client.post(reverse("delete_invoice", args=[invoices[0].id]), follow=True)
        self.assertFalse(Invoice.objects.filter(id__in=[invoice.id for invoice in invoices]).exists())
        self.assertFalse(
            CAPDiscountAmount.objects.filter(
                cap_discount__account=self.project.account, year=two_month_ago_date.year, month=two_month_ago_date.month
            ).exists()
        )
        # CAP discount should still exist
        self.assertTrue(CAPDiscount.objects.filter(account=self.project.account).exists())
        # Now delete previous one, we have nothing left
        self.client.post(reverse("delete_invoice", args=[first_invoices[0].id]), follow=True)
        self.assertRaises(Invoice.DoesNotExist, Invoice.objects.get, pk=first_invoices[0].id)
        self.assertFalse(CAPDiscountAmount.objects.all().exists())
        self.assertFalse(CAPDiscount.objects.all().exists())

    def test_void_invoice_without_cap(self):
        accounting = User.objects.create(
            first_name="Staffy", last_name="McStaffer", username="staffy", is_accounting_officer=True
        )
        # Our cap is at 100, and discount 25%. Set start 2 month ago
        two_month_ago_date = timezone.now() - relativedelta(months=2)
        self.cap_configuration.start = two_month_ago_date
        self.cap_configuration.save()
        # Add charges 2 months ago
        end = two_month_ago_date - timedelta(minutes=20)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=self.project, start=start, end=end
        )
        # Add new charges to different project, and different account (not capped -> industry).
        new_project = Project.objects.create(name="new proj", account=Account.objects.create(name="Test Account 2"))
        category = RateCategory.objects.get(name="Industry")
        tool_usage = RateType.objects.get(type="TOOL_USAGE")
        Rate.objects.create(category=category, type=tool_usage, tool=self.tool, amount="30.00")
        new_project.projectbillingdetails = ProjectBillingDetails.objects.create(project=new_project, category=category)
        end = two_month_ago_date - timedelta(minutes=5)
        start = end - timedelta(hours=2)
        UsageEvent.objects.create(
            user=self.user, operator=self.user, tool=self.tool, project=new_project, start=start, end=end
        )
        # Generate invoices 2 months ago
        invoices = self.generate_invoice(two_month_ago_date, self.project.account)
        invoices.extend(self.generate_invoice(two_month_ago_date, new_project.account))
        self.assertEqual(len(invoices), 2)
        self.client.force_login(accounting)
        self.client.post(reverse("delete_invoice", args=[invoices[0].id]), follow=True)
        self.assertRaises(Invoice.DoesNotExist, Invoice.objects.get, pk=invoices[0].id)
        self.assertTrue(Invoice.objects.get(pk=invoices[1].id))

    def test_multi_tier_discount(self):
        cap_discount = self.cap_configuration.get_or_create_cap_discount(
            account=self.project.account, username=None, start=timezone.now()
        )
        # CAP is at 25% for > 100
        calculator = AccountDiscountCalculator(timezone.now())
        self.assertEqual(calculator.calculate_discount(50, 50, cap_discount), 0)
        self.assertEqual(calculator.calculate_discount(100, 40, cap_discount), -10)
        self.assertEqual(calculator.calculate_discount(100, 100, cap_discount), -25)
        # Add new tier for over 400 -> 50%
        cap_discount.capdiscounttier_set.add(
            CAPDiscountTier.objects.create(cap_discount=cap_discount, amount=400, discount=50)
        )
        self.assertEqual(calculator.calculate_discount(50, 50, cap_discount), 0)
        self.assertEqual(calculator.calculate_discount(100, 40, cap_discount), -10)
        self.assertEqual(calculator.calculate_discount(100, 100, cap_discount), -25)
        self.assertEqual(calculator.calculate_discount(300, 100, cap_discount), -25)
        # discount -> 100 * 50% (50) + 100 * 25% (25) = -75
        self.assertEqual(calculator.calculate_discount(300, 200, cap_discount), -75)
        # discount -> 200 * 50% (100) + 100 * 25% (25) = -125
        self.assertEqual(calculator.calculate_discount(300, 300, cap_discount), -125)
        # Add new tier for over 400 -> 50%
        cap_discount.capdiscounttier_set.add(
            CAPDiscountTier.objects.create(cap_discount=cap_discount, amount=600, discount=75)
        )
        self.assertEqual(calculator.calculate_discount(300, 300, cap_discount), -125)
        self.assertEqual(calculator.calculate_discount(50, 50, cap_discount), 0)
        self.assertEqual(calculator.calculate_discount(100, 40, cap_discount), -10)
        self.assertEqual(calculator.calculate_discount(100, 100, cap_discount), -25)
        self.assertEqual(calculator.calculate_discount(300, 100, cap_discount), -25)
        self.assertEqual(calculator.calculate_discount(300, 200, cap_discount), -75)
        self.assertEqual(calculator.calculate_discount(300, 300, cap_discount), -125)
        # discount -> 500 * 75% (375) + 200 * 50% (100) + 300 * 25% (75) = -550
        self.assertEqual(calculator.calculate_discount(100, 1000, cap_discount), -550)

    def generate_invoice(self, invoice_date, account: Account = None) -> Optional[List[Invoice]]:
        invoice_configuration = InvoiceConfiguration.first_or_default()
        if not invoice_configuration.id:
            invoice_configuration.save()
        month = invoice_date.strftime("%B %Y")
        account = account or self.project.account
        return processor.generate_invoice_for_account(month, account, invoice_configuration, self.user)
