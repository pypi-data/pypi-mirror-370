from _decimal import Decimal
from datetime import date, datetime
from typing import List

from NEMO.models import (
    Account,
    Project,
)
from NEMO.utilities import RecurrenceFrequency, new_model_copy
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.forms import CheckboxInput, HiddenInput
from django.test import TestCase
from django.utils import timezone

from NEMO_billing.admin import CustomChargeAdminForm
from NEMO_billing.cap_discount.models import CAPDiscount, CAPDiscountAmount, CAPDiscountConfiguration, CAPDiscountTier
from NEMO_billing.invoices.models import BillableItemType, Invoice, InvoiceConfiguration
from NEMO_billing.invoices.processors import invoice_data_processor_class as processor
from NEMO_billing.models import CoreFacility, CustomCharge
from NEMO_billing.rates.models import RateCategory
from NEMO_billing.tests.cap.test_cap_utilities import (
    add_charges_of_type,
    create_items,
    delete_all_billables,
    get_other_billable_types,
)
from NEMO_billing.tests.test_utilities import basic_data


class TestCapAmount(TestCase):
    def setUp(self) -> None:
        self.user, self.project, self.tool, self.area = basic_data(set_rate_category=True)
        cap_configuration = CAPDiscountConfiguration(rate_category=self.project.projectbillingdetails.category)
        cap_configuration.reset_frequency = RecurrenceFrequency.YEARLY.value
        cap_configuration.start = date.today()
        cap_configuration.start_on_first_charge = False
        self.assertRaises(ValidationError, cap_configuration.full_clean)
        cap_configuration.charge_types = BillableItemType.TOOL_USAGE.value
        cap_configuration.full_clean()
        cap_configuration.save()
        cap_configuration.capdiscounttier_set.set(
            [
                CAPDiscountTier.objects.create(
                    cap_discount_configuration=cap_configuration, amount=Decimal("100"), discount=Decimal("100")
                )
            ]
        )
        self.cap_configuration: CAPDiscountConfiguration = CAPDiscountConfiguration.objects.get(pk=cap_configuration.pk)
        self.tool, self.area, self.consumable, self.staff = create_items()

    def test_cap_config_required_fields(self):
        cap_config = self.cap_configuration
        # right now it's clean
        cap_config.full_clean()
        # No limit amount
        cap_tier = cap_config.capdiscounttier_set.first()
        cap_tier.amount = None
        self.assertRaises(ValidationError, cap_tier.full_clean)
        # limit of 0
        cap_tier.amount = Decimal(0)
        self.assertRaises(ValidationError, cap_tier.full_clean)
        cap_tier.amount = Decimal("1")
        cap_tier.full_clean()
        # No discount
        cap_tier.discount = None
        self.assertRaises(ValidationError, cap_tier.full_clean)
        # This is intentional, since it could be a higher tier with no discount
        cap_tier.discount = Decimal(0)
        cap_tier.full_clean()
        # Cannot have more than 100% discount
        cap_tier.discount = Decimal("101")
        self.assertRaises(ValidationError, cap_tier.full_clean)
        # 100% ok
        cap_tier.discount = Decimal("100")
        cap_tier.full_clean()
        # Start date is required when not starting on first eligible charge
        cap_config.start = None
        cap_config.start_on_first_charge = False
        self.assertRaises(ValidationError, cap_config.full_clean)
        cap_config.start = datetime.now()
        cap_config.full_clean()
        # Year set but not month
        cap_config.start_year = 2022
        cap_config.start_month = None
        self.assertRaises(ValidationError, cap_config.full_clean)
        # Month set but not year
        cap_config.start_year = None
        cap_config.start_month = 2
        self.assertRaises(ValidationError, cap_config.full_clean)
        # Start not set but start of first charge is -> OK
        cap_config.start = None
        cap_config.start_on_first_charge = True
        cap_config.full_clean()
        # Now get a CAP and check required fields
        cap = cap_config.get_or_create_cap_discount(
            account=self.project.account, username=self.user.username, start=date.today()
        )
        # override in the past not okay
        cap.next_reset_override = date.today() - relativedelta(months=1)
        self.assertRaises(ValidationError, cap.full_clean)
        # today should be ok
        cap.next_reset_override = date.today()
        cap.full_clean()
        # future is ok
        cap.next_reset_override = date.today() + relativedelta(months=14)
        cap.full_clean()
        # No account
        cap.account = None
        self.assertRaises(ValidationError, cap.full_clean)
        cap.account = self.project.account
        cap.full_clean()
        # User has to belong to account
        new_account = Account.objects.create(name="new account")
        cap.account = new_account
        self.assertRaises(ValidationError, cap.full_clean)

    def test_cap_uniqueness(self):
        # Simulate having a cap
        cap = self.cap_configuration.get_or_create_cap_discount(
            account=self.project.account, username=self.user.username, start=date.today()
        )
        # This new cap has same user/account combination as cap (with no core facility)
        new_cap = CAPDiscount(
            configuration=self.cap_configuration,
            user=self.user,
            account=self.project.account,
            charge_types=BillableItemType.TOOL_USAGE.value,
            reset_frequency=RecurrenceFrequency.YEARLY.value,
        )
        with transaction.atomic():
            self.assertRaises(IntegrityError, new_cap.save)
        new_project = Project.objects.create(name="p", account=Account.objects.create(name="new account"))
        self.user.projects.add(new_project)
        new_cap.account = new_project.account
        new_cap.save()
        CAPDiscountTier.objects.create(cap_discount=new_cap, amount=Decimal("5"), discount=Decimal("50"))
        facility = CoreFacility.objects.create(name="facility_1")
        # Set facility on original
        self.cap_configuration.core_facilities.set([facility])
        # Create new config without facility
        new_config = new_model_copy(self.cap_configuration)
        new_config.save()
        # Save, no problems
        new_config.core_facilities.clear()
        # Copy cap but without facility, should be fine
        new_cap.configuration = new_config
        new_cap.account = self.project.account
        new_cap.user = self.user
        new_cap.save()
        # Set same facility, should break
        with transaction.atomic():
            self.assertRaises(IntegrityError, new_config.core_facilities.set, [facility])
        # Set one of the same facilities, should break
        facility_2 = CoreFacility.objects.create(name="facility_2")
        with transaction.atomic():
            self.assertRaises(IntegrityError, new_config.core_facilities.set, [facility, facility_2])
        # Set only facility 2, should be fine
        new_config.core_facilities.set([facility_2])
        # Now try to add same facility 2 to first config, should break
        with transaction.atomic():
            self.assertRaises(IntegrityError, self.cap_configuration.core_facilities.add, facility_2)
        # Clear the first one, all good
        self.cap_configuration.core_facilities.clear()
        # Clear the second one, should break
        with transaction.atomic():
            self.assertRaises(IntegrityError, new_config.core_facilities.clear)
        # Create a new one without facilities, should break
        with transaction.atomic():
            self.assertRaises(
                IntegrityError,
                CAPDiscountConfiguration.objects.create,
            )

    def test_reset(self):
        # Simulate previously created CAP
        cap = self.cap_configuration.get_or_create_cap_discount(
            account=self.project.account, username=self.user.username, start=date.today()
        )
        # Change a few things in the cap configuration, the cap itself should not change until reset
        cap_configuration = self.cap_configuration
        cap_tier = cap_configuration.capdiscounttier_set.first()
        cap_tier.amount = Decimal(200)
        cap_tier.discount = Decimal(50)
        cap_tier.save()
        cap_configuration.charge_types = BillableItemType.AREA_ACCESS.value
        cap_configuration.reset_interval = 2
        cap_configuration.reset_frequency = RecurrenceFrequency.MONTHLY.value
        cap_configuration.save()
        # Check before reset
        cap = self.cap_configuration.get_or_create_cap_discount(
            account=self.project.account, username=self.user.username, start=date.today()
        )
        self.assertEqual(cap.capdiscounttier_set.first().amount, 100)
        self.assertEqual(cap.capdiscounttier_set.first().discount, 100)
        self.assertEqual(cap.billable_charge_types, [BillableItemType.TOOL_USAGE])
        self.assertEqual(cap.reset_interval, 1)
        self.assertEqual(cap.reset_frequency, RecurrenceFrequency.YEARLY.value)
        # Prepare for reset with override
        cap.next_reset_override = timezone.now().date()
        cap.reset()
        # Check after reset
        cap_after_reset = self.cap_configuration.get_or_create_cap_discount(
            account=self.project.account, username=self.user.username, start=date.today()
        )
        self.assertFalse(cap_after_reset.next_reset_override)
        self.assertEqual(cap_after_reset.capdiscounttier_set.first().amount, 200)
        self.assertEqual(cap_after_reset.capdiscounttier_set.first().discount, 50)
        self.assertEqual(cap_after_reset.billable_charge_types, [BillableItemType.AREA_ACCESS])
        self.assertEqual(cap_after_reset.reset_interval, 2)
        self.assertEqual(cap_after_reset.reset_frequency, RecurrenceFrequency.MONTHLY.value)

    def test_next_reset_override(self):
        cap = self.cap_configuration.get_or_create_cap_discount(
            account=self.project.account, username=self.user.username, start=date.today()
        )
        self.assertEqual(cap.next_reset().date(), cap.start + relativedelta(years=1))
        cap.next_reset_override = cap.start + relativedelta(months=1)
        cap.save()
        cap = CAPDiscount.objects.get(pk=cap.pk)
        self.assertTrue(cap.next_reset_override)
        self.assertEqual(cap.next_reset().date(), cap.next_reset_override)
        cap.reset()
        cap = CAPDiscount.objects.get(pk=cap.pk)
        self.assertFalse(cap.next_reset_override)

    def test_next_reset_override_first_usage(self):
        self.cap_configuration.start_on_first_charge = True
        self.cap_configuration.save()
        cap = self.cap_configuration.get_or_create_cap_discount(
            account=self.project.account,
            username=self.user.username,
            start=date.today(),
        )
        self.assertEqual(cap.next_reset().date(), cap.start + relativedelta(years=1))
        cap.next_reset_override = cap.start + relativedelta(months=1)
        previous_override = cap.next_reset_override
        cap.save()
        cap = CAPDiscount.objects.get(pk=cap.pk)
        self.assertTrue(cap.next_reset_override)
        self.assertEqual(cap.next_reset().date(), cap.next_reset_override)
        cap.reset()
        cap = CAPDiscount.objects.get(pk=cap.pk)
        # New start date should be set to last reset override (since start on first usage is set)
        self.assertEqual(cap.start, previous_override)
        self.assertFalse(cap.next_reset_override)

    def test_custom_charge_cap_eligible_field(self):
        with self.modify_settings(INSTALLED_APPS={"prepend": "NEMO_billing.cap_discount"}):
            form = CustomChargeAdminForm()
            self.assertFalse(form.fields["cap_eligible"].disabled)
            self.assertIsInstance(form.fields["cap_eligible"].widget, CheckboxInput)
        with self.modify_settings(INSTALLED_APPS={"remove": "NEMO_billing.cap_discount"}):
            form = CustomChargeAdminForm()
            self.assertTrue(form.fields["cap_eligible"].disabled)
            self.assertIsInstance(form.fields["cap_eligible"].widget, HiddenInput)

    def test_cap_eligible_custom_charge(self):
        facility = CoreFacility.objects.create(name="facility")
        # Add custom charge types to CAP entity
        self.cap_configuration.charge_types = [BillableItemType.TOOL_USAGE.value, BillableItemType.CUSTOM_CHARGE.value]
        self.cap_configuration.save()
        # Create cap eligible charge for different rate category. There is no matching CAPDiscount. It should break if cap discount is installed
        charge_date = timezone.now()
        self.project.projectbillingdetails.category = RateCategory.objects.get(name="Industry")
        self.project.projectbillingdetails.save()
        custom_charge = CustomCharge(
            name="custom",
            customer=self.user,
            creator=self.staff,
            project=self.project,
            date=charge_date,
            amount=10,
            cap_eligible=True,
        )
        with self.modify_settings(INSTALLED_APPS={"prepend": "NEMO_billing.cap_discount"}):
            self.assertRaises(ValidationError, custom_charge.full_clean)
            # put Academia back
            self.project.projectbillingdetails.category = RateCategory.objects.get(name="Academia")
            self.project.projectbillingdetails.save()
            custom_charge.full_clean()
            self.cap_configuration.core_facilities.set([facility])
            # No existing cap with no facility
            self.assertRaises(ValidationError, custom_charge.full_clean)
            custom_charge.core_facility = facility
            # now ok
            custom_charge.full_clean()
            # reset
            self.cap_configuration.core_facilities.clear()
        with self.modify_settings(INSTALLED_APPS={"remove": "NEMO_billing.cap_discount"}):
            # reset
            custom_charge.core_facility = None
            # Even with staff as custom charge, it doesn't matter since cap_discount is not installed
            self.staff.projects.add(self.project)
            custom_charge.customer = self.staff
            custom_charge.full_clean()
            # also fine with different facility
            custom_charge.core_facility = facility
            custom_charge.full_clean()

    def test_cap_amounts(self):
        # test uniqueness
        # get or create will initialize an amount for us
        cap = self.cap_configuration.get_or_create_cap_discount(
            account=self.project.account, username=self.user.username, start=date.today()
        )
        # Should break because it's not unique (month/year)
        new_amount = CAPDiscountAmount(
            cap_discount=cap, year=date.today().year, month=date.today().month, start=0, end=100
        )
        self.assertRaises(ValidationError, new_amount.full_clean)
        # All good with date of last month
        last_month = date.today() - relativedelta(months=1)
        new_amount = CAPDiscountAmount(cap_discount=cap, year=last_month.year, month=last_month.month, start=0, end=100)
        new_amount.full_clean()
        # Copy previous cap and re-save it, should fail this time with unique issue on CAP user/account combination
        new_cap = new_model_copy(cap)
        with transaction.atomic():
            self.assertRaises(IntegrityError, new_cap.save)
        # All good now with same date but different cap discount object
        new_cap.account = Account.objects.create(name="new acc")
        new_cap.save()
        new_amount = CAPDiscountAmount(
            cap_discount=new_cap, year=last_month.year, month=last_month.month, start=0, end=100
        )
        new_amount.full_clean()

    def test_set_start_not_needed(self):
        # If start date, nothing happens
        cap_configuration = self.cap_configuration
        cap_configuration.start = date.today()
        cap_configuration.save()
        add_charges_of_type(self, [BillableItemType.TOOL_USAGE], timezone.now())
        self.generate_invoice(timezone.now())
        cap_configuration = CAPDiscount.objects.get(pk=cap_configuration.pk)
        # But the date is set to today's month and year
        self.assertEqual(date.today().month, cap_configuration.start_month)
        self.assertEqual(date.today().year, cap_configuration.start_year)

    def test_all_types_of_charges(self):
        # Test each charge
        for billable_type in BillableItemType:
            with self.subTest(billable_type.name):
                self.charges_subtest([billable_type])
                delete_all_billables()
        # Test combination of charges
        for i in range(1, 8):
            for j in range(i + 1, 8):
                with self.subTest(f"{BillableItemType(i).name}-{BillableItemType(j).name}"):
                    self.charges_subtest([BillableItemType(i), BillableItemType(j)])
                    delete_all_billables()

    def charges_subtest(self, billable_charge_types: List[BillableItemType]):
        # Reset start date and amounts
        cap_configuration = self.cap_configuration
        cap_configuration.start = None
        cap_configuration.start_on_first_charge = True
        cap_configuration.charge_types = ",".join([str(t.value) for t in billable_charge_types])
        cap_configuration.full_clean()
        cap_configuration.save()
        CAPDiscountAmount.objects.filter(cap_discount__configuration=cap_configuration).delete()
        CAPDiscount.objects.filter(configuration=cap_configuration).delete()
        # If the charge end date is earlier than invoice start date, nothing happens
        Invoice.objects.all().delete()
        end = timezone.now() - relativedelta(months=1)
        self.assertTrue(end < timezone.now())
        add_charges_of_type(self, cap_configuration.billable_charge_types, end)
        self.generate_invoice(timezone.now())
        cap_qs = CAPDiscount.objects.filter(configuration=cap_configuration)
        self.assertFalse(cap_qs.exists())
        # If the charge end date is newer than invoice end date, nothing happens
        Invoice.objects.all().delete()
        two_months_ago_date = timezone.now() - relativedelta(months=2)
        self.assertTrue(end > two_months_ago_date)
        add_charges_of_type(self, cap_configuration.billable_charge_types, end)
        self.generate_invoice(two_months_ago_date)
        cap_qs = CAPDiscount.objects.filter(configuration=cap_configuration)
        self.assertFalse(cap_qs.exists())
        # If charge is a from different type, nothing happens
        # Add all other types of charges
        Invoice.objects.all().delete()
        today = timezone.now()
        add_charges_of_type(self, get_other_billable_types(cap_configuration.billable_charge_types), today)
        self.generate_invoice(today)
        cap_qs = CAPDiscount.objects.filter(configuration=cap_configuration)
        self.assertFalse(cap_qs.exists())
        # If it's an eligible charge, start date should be set to today's month
        Invoice.objects.all().delete()
        end = today
        add_charges_of_type(self, cap_configuration.billable_charge_types, end)
        self.generate_invoice(today)
        cap = CAPDiscount.objects.get(configuration=cap_configuration)
        self.assertEqual(cap.start_month, today.month)
        self.assertEqual(cap.start_year, today.year)

    def generate_invoice(self, invoice_date):
        invoice_configuration = InvoiceConfiguration.first_or_default()
        if not invoice_configuration.id:
            invoice_configuration.save()
        processor.generate_invoice_for_account(
            invoice_date.strftime("%B %Y"), self.project.account, invoice_configuration, self.user
        )

    def test_voiding_invoices(self):
        # we should only let the latest invoice be voided. then the previous one can be too, etc.
        # make sure the relevant cap amounts are voided as well or deleted?
        # the problem is that some charges already hit cap for project 2 based on project 1's charges, so it's bad to go back
        pass
