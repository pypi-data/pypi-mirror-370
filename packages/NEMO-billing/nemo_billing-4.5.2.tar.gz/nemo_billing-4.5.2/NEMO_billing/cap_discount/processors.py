from _decimal import Decimal
from datetime import date, datetime, time
from logging import getLogger
from typing import Dict, Iterable, List, Optional, Tuple, Union

from NEMO.models import Account, Project
from NEMO.utilities import get_month_timeframe, localize
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.admin.utils import get_deleted_objects
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest
from django.utils import timezone

from NEMO_billing.cap_discount.customization import CAPDiscountCustomization
from NEMO_billing.cap_discount.exceptions import MissingCAPAmountException, NotLatestInvoiceException
from NEMO_billing.cap_discount.models import CAPDiscount, CAPDiscountAmount, CAPDiscountConfiguration, CAPDiscountTier
from NEMO_billing.invoices.customization import InvoiceCustomization
from NEMO_billing.invoices.models import (
    BillableItemType,
    Invoice,
    InvoiceConfiguration,
    InvoiceDetailItem,
    InvoiceSummaryItem,
)
from NEMO_billing.invoices.processors import (
    FullInvoice,
    InvoiceDataProcessor,
    billable_to_invoice_detail_item,
    get_account_invoices,
)
from NEMO_billing.rates.models import RateCategory
from NEMO_billing.utilities import round_decimal_amount

processors_logger = getLogger(__name__)


error_extra_tags = "data-speed=30000 data-trigger=manual"


# Class to hold information about the discounts for an account, split by projects/users/core facilities
class AccountDiscountCalculator:
    def __init__(self, start_date: date):
        self.start_date = start_date
        # We are creating a dict of rate_category -> tuple(facility_names) -> usernames -> cap discount objects
        self.cap_discounts: Dict[str, Dict[tuple, Dict[str, CAPDiscount]]] = {}

    def add_item(self, item: InvoiceDetailItem):
        # This assumes we are getting the items in order of end date first, so we can add up amounts
        project = item.invoice.project_details.project
        cap_discount = self.get_or_create_cap(project, item)
        if cap_discount and item_cap_discount_match(item, cap_discount):
            discount_amount = self.calculate_discount(cap_discount.tmp_current_amount, item.amount, cap_discount)
            if discount_amount:
                prj_id = item.invoice.project_details.project.id
                project_facility_discount = cap_discount.tmp_project_discounts.setdefault(prj_id, {}).setdefault(
                    item.core_facility, Decimal(0)
                )
                item.discount = discount_amount
                cap_discount.tmp_project_discounts[prj_id][item.core_facility] = (
                    project_facility_discount + item.discount
                )
            cap_discount.tmp_current_amount += item.amount

    def calculate_discount(self, current_total, item_amount, cap_discount: CAPDiscount) -> Decimal:
        total_discount = Decimal(0)
        # We need to order by descending tier amount. This is really important for the algorithm to work
        tier_discounts = list(cap_discount.capdiscounttier_set.order_by("-amount"))
        # We are initializing the remaining at the current amount
        # Then we will apply the higher tier discount if applicable,
        # And subtract the amount until we have nothing remaining
        remaining = item_amount
        for i, tier in enumerate(tier_discounts):
            tier: CAPDiscountTier = tier
            if remaining and current_total + remaining > tier.amount:
                amount_for_discount = remaining - max(tier.amount - current_total, Decimal(0))
                total_discount += amount_for_discount * tier.discount_amount()
                remaining -= amount_for_discount
        return round_decimal_amount(total_discount)

    def get_or_create_cap(self, project: Project, item: InvoiceDetailItem) -> Optional[CAPDiscount]:
        core_facility = item.core_facility
        username = item.user
        rate_category = project.projectbillingdetails.category
        rate_category_dict: Dict[tuple, Dict[str, CAPDiscount]] = self.cap_discounts.setdefault(rate_category.name, {})
        try:
            config = CAPDiscountConfiguration.objects.get(
                rate_category=rate_category, core_facilities__name=core_facility
            )
            facility_names = config.core_facility_names or (None,)
            facility_dict: Dict[str, CAPDiscount] = rate_category_dict.setdefault(facility_names, {})
            username = username if config.split_by_user else None
            if username in facility_dict:
                return facility_dict.get(username)
            # Only create if it is an eligible charge
            elif item_cap_discount_match(item, config):
                cap_discount: CAPDiscount = config.get_or_create_cap_discount(
                    account=project.account, username=username, start=self.start_date
                )
                # Set tmp current amount
                cap_discount.tmp_current_amount = CAPDiscountAmount.objects.get(
                    cap_discount=cap_discount, month=self.start_date.month, year=self.start_date.year
                ).start
                return facility_dict.setdefault(username, cap_discount)
        except CAPDiscountConfiguration.DoesNotExist:
            processors_logger.debug(
                f"No CAP configuration found for rate: {rate_category} and core facility: {core_facility}"
            )

    def get_discounts_for_project(self, rate_category: RateCategory, core_facility: str) -> List[CAPDiscount]:
        # Returns the facility discounts for each user
        total_cap_discounts: List[CAPDiscount] = []
        for core_facility_names, cap_discounts_dict in self.cap_discounts.get(rate_category.name, {}).items():
            if core_facility in core_facility_names:
                total_cap_discounts.extend(cap_discounts_dict.values())
        return total_cap_discounts

    def all_cap_discounts(self) -> List[CAPDiscount]:
        return [
            value
            for rate_category_dict in self.cap_discounts.values()
            for facility_dict in rate_category_dict.values()
            for value in facility_dict.values()
            if rate_category_dict and facility_dict
        ]


class CAPDiscountInvoiceDataProcessor(InvoiceDataProcessor):
    # Do all this in a transaction so everything gets rolled back if an error happened
    @transaction.atomic
    def generate_invoice_for_account(self, month, account, configuration, user, raise_if_exists=False) -> List[Invoice]:
        capped_invoices: List[FullInvoice] = []
        non_capped_invoices: List[FullInvoice] = []
        if not InvoiceCustomization.get_bool("invoice_skip_inactive_accounts") or account.active:
            # Overriding this, so we can deal with discounts and save all invoices at the end
            start, end = get_month_timeframe(month)
            # First let's check that cap discounts have been correctly generated until now
            # And initialize new amounts for this month
            check_and_initialize_monthly_cap_amounts(account, start)

            # Now create our cap calculator helper
            discount_calculator = AccountDiscountCalculator(start.date())

            # Go through the generation process, and add all items to account details list
            all_account_details: List[InvoiceDetailItem] = []
            account_filter = Q(project__account_id=account.id)
            all_billable_items = self.get_billable_items(
                start, end, configuration, account_filter, account_filter, account_filter
            )
            projects = account.project_set.all()
            if InvoiceCustomization.get_bool("invoice_skip_inactive_projects"):
                projects = projects.filter(active=True)
            for project in projects:
                billables = [billable for billable in all_billable_items if billable.project == project]
                invoice = self.generate_invoice(start, end, project, configuration, user, billables, raise_if_exists)
                if invoice:
                    # do not run cap calculations for prepaid projects
                    if hasattr(project, "projectprepaymentdetail"):
                        non_capped_invoices.append(invoice)
                    else:
                        capped_invoices.append(invoice)
                        all_account_details.extend(invoice.detail_items)

            if all_account_details:
                # Sort account details by end date. This is very IMPORTANT to get discounts right
                all_account_details.sort(key=lambda x: x.end)
                # Go through all account charges to figure out the discounts
                for detail in all_account_details:
                    discount_calculator.add_item(detail)
                # Now let's update the CAP entities with the total charges for this account
                for cap_discount in discount_calculator.all_cap_discounts():
                    amount = CAPDiscountAmount.objects.get(
                        cap_discount=cap_discount, year=start.year, month=start.month
                    )
                    amount.end = cap_discount.tmp_current_amount
                    amount.save(update_fields=["end"])

            # Save all the invoices now
            self.save_invoices(capped_invoices, discount_calculator)
            # Only save regular invoices after everything went well for CAP invoices
            for invoice in non_capped_invoices:
                invoice.save()
        return [full_invoice.invoice for full_invoice in (capped_invoices + non_capped_invoices)]

    def save_invoices(self, full_invoices: List[FullInvoice], discount_calculator: AccountDiscountCalculator = None):
        for full_invoice in full_invoices:
            # Pass calculator through the invoice, so we can retrieve it later
            full_invoice.invoice.discount_calculator = discount_calculator
            # Recalculate summaries with the discounts
            full_invoice.summary_items = self.get_invoice_summary_items(full_invoice.invoice, full_invoice.detail_items)
            full_invoice.save()

    # Override this method, to check if we need to deal with discounts or not
    def get_summary_items_for_facility(self, invoice: Invoice, core_facility: str, details) -> List[InvoiceSummaryItem]:
        cap_discounts = []

        calc: AccountDiscountCalculator = getattr(invoice, "discount_calculator", None)
        if calc:
            rate_category = invoice.project_details.category
            cap_discounts: List[CAPDiscount] = calc.get_discounts_for_project(rate_category, core_facility)

        if not cap_discounts:
            # If we don't have any discounts, return original function
            return super().get_summary_items_for_facility(invoice, core_facility, details)
        else:
            # Otherwise re-generate summary items with discounts
            return self.get_summary_items_for_facility_with_discounts(invoice, core_facility, details, cap_discounts)

    # This is our new version with the discount calculation
    def get_summary_items_for_facility_with_discounts(
        self, invoice: Invoice, core_facility: str, details, cap_discounts: List[CAPDiscount]
    ) -> List[InvoiceSummaryItem]:
        # Re-generate summary items
        facility_summaries: List[InvoiceSummaryItem] = []
        for billable_type in BillableItemType:
            items = [item for item in details if item.item_type == billable_type.value]
            facility_summaries.extend(self.get_recap_usage_summary(invoice, core_facility, items))

        total_discount = Decimal(0)
        for cap_discount in cap_discounts:
            discount_amt = cap_discount.tmp_project_discounts.get(invoice.project_details.project.id, {}).get(
                core_facility
            )
            if discount_amt and discount_amt != 0:
                discount_name = f"{cap_discount.configuration.rate_category.name}{'/' + cap_discount.user.username if cap_discount.user else ''} CAP Discount"
                f_discount = InvoiceSummaryItem(invoice=invoice, name=discount_name, core_facility=core_facility)
                f_discount.summary_item_type = InvoiceSummaryItem.InvoiceSummaryItemType.DISCOUNT
                f_discount.amount = round_decimal_amount(discount_amt)
                facility_summaries.append(f_discount)
                total_discount += f_discount.amount

        facility_subtotal = InvoiceSummaryItem(invoice=invoice, name="Subtotal", core_facility=core_facility)
        facility_subtotal.summary_item_type = InvoiceSummaryItem.InvoiceSummaryItemType.SUBTOTAL
        non_waived_items = [item for item in details if not item.waived]
        facility_subtotal.amount = round_decimal_amount(sum(item.amount for item in non_waived_items) + total_discount)
        facility_summaries.append(facility_subtotal)

        return facility_summaries

    @transaction.atomic
    def delete_invoice(self, invoice: Invoice, request: HttpRequest):
        # NOTE: For now, we are deleting all invoices for this account, even non-capped ones
        # if this invoice has a CAP Discount associated with its account,
        # delete all the other account invoices and CAP amounts for the month.
        # This will force to re-generate all the invoices and CAP calculation.
        invoice_account = invoice.project_details.project.account
        invoice_year, invoice_month = invoice.start.year, invoice.start.month
        try:
            delete_associated_amounts(invoice_account, invoice_year, invoice_month, request)
        except NotLatestInvoiceException as e:
            messages.error(request, e.msg, extra_tags=error_extra_tags)
            return
        # the super method will delete all other account invoices, so we are good
        super().delete_invoice(invoice, request)

    @transaction.atomic
    def void_invoice(self, invoice: Invoice, request: HttpRequest):
        invoice_account = invoice.project_details.project.account
        invoice_year, invoice_month = invoice.start.year, invoice.start.month
        try:
            delete_associated_amounts(invoice_account, invoice_year, invoice_month, request)
        except NotLatestInvoiceException as e:
            messages.error(request, e.msg, extra_tags=error_extra_tags)
            return
        # the super method will void all other account invoices, so we are good
        super().void_invoice(invoice, request)

    def get_deleted_objects(self, invoices: Iterable[Invoice], request: HttpRequest, admin_site):
        # gather all related objects to delete: other invoices, cap discounts, cap discount amounts
        related_invoices = []
        related_discounts = []
        related_amounts = []
        try:
            for invoice in invoices:
                invoice_account = invoice.project_details.project.account
                invoice_year, invoice_month = invoice.start.year, invoice.start.month
                related_invoices.extend(get_account_invoices(invoice_account, invoice_year, invoice_month))
                related_amounts.extend(get_amounts_to_delete(invoice_account, invoice_year, invoice_month))
        except NotLatestInvoiceException as e:
            return [], {}, set(), [e.msg]
        invoice_deleted_objects = get_deleted_objects(related_invoices, request, admin_site)
        # We might need to also delete some CAPDiscounts if the amount was the first
        for cap_amount in related_amounts:
            if cap_amount.cap_discount.earliest_amount() == cap_amount:
                related_discounts.append(cap_amount.cap_discount)
                related_amounts.remove(cap_amount)
        amount_deleted_objects = get_deleted_objects(related_amounts, request, admin_site)
        discount_deleted_objects = get_deleted_objects(related_discounts, request, admin_site)
        return (
            invoice_deleted_objects[0] + amount_deleted_objects[0] + discount_deleted_objects[0],
            {**invoice_deleted_objects[1], **amount_deleted_objects[1], **discount_deleted_objects[1]},
            invoice_deleted_objects[2],
            invoice_deleted_objects[2],
        )

    def estimated_charges_since_last_update(self, cap_discount: CAPDiscount) -> Decimal:
        latest_amount = cap_discount.latest_amount()
        start_since_update = (
            latest_amount.amount_date + relativedelta(months=1)
            if latest_amount
            else date(timezone.now().year, timezone.now().month, 1)
        )
        customer_filter = Q(project__account=cap_discount.account)
        user_filter = Q(project__account=cap_discount.account)
        trainee_filter = Q(project__account=cap_discount.account)
        if cap_discount.user:
            customer_filter = customer_filter & Q(customer=cap_discount.user)
            user_filter = user_filter & Q(user=cap_discount.user)
            trainee_filter = trainee_filter & Q(trainee=cap_discount.user)
        config = InvoiceConfiguration.first_or_default()
        items = self.get_billable_items(
            localize(datetime.combine(start_since_update, time())),
            timezone.now(),
            config,
            customer_filter,
            user_filter,
            trainee_filter,
            raise_no_rate=False,
        )
        detail_items: List[InvoiceDetailItem] = []
        for item in items:
            # exceptional case here where we need to create a "fake" invoice,
            # so we can match items correctly
            invoice = Invoice()
            invoice.project_details = item.project.projectbillingdetails
            detail_items.append(billable_to_invoice_detail_item(item, invoice=invoice))
        return Decimal(sum(item.amount for item in detail_items if item_cap_discount_match(item, cap_discount)))


def item_cap_discount_match(item: InvoiceDetailItem, cap: Union[CAPDiscount, CAPDiscountConfiguration]):
    # function to check eligible/matching items for CAPDiscount or CAPDiscountConfiguration
    configuration = cap
    cap_match = True
    if isinstance(cap, CAPDiscount):
        cap_match = item.invoice.project_details.project.account == cap.account
        if cap.configuration.split_by_user:
            cap_match = cap_match and item.user == cap.user.username
        configuration = cap.configuration

    configuration_core_facilities: Tuple[str] = configuration.core_facility_names or (None,)
    item_type = BillableItemType(item.item_type)

    # Check if tool is not excluded from CAP
    tool_excluded = False
    excluded_tool_ids = CAPDiscountCustomization.get_excluded_tool_ids()
    if excluded_tool_ids:
        if item_type in [BillableItemType.TOOL_USAGE, BillableItemType.MISSED_RESERVATION, BillableItemType.TRAINING]:
            if item.content_object and item.content_object.tool:
                tool_excluded = item.content_object.tool.id in excluded_tool_ids
    if item_type == BillableItemType.STAFF_CHARGE:
        # TODO: not sure here how to figure out if the tool is excluded since it's not set on the item
        pass

    # Only include cap eligible Custom Charges
    custom_charge_included = True
    if item_type == BillableItemType.CUSTOM_CHARGE:
        custom_charge_included = item.content_object and item.content_object.cap_eligible

    return (
        item_type in cap.billable_charge_types
        and not item.waived
        and not tool_excluded
        and custom_charge_included
        and item.invoice.project_details.category == configuration.rate_category
        and item.core_facility in configuration_core_facilities
        and cap_match
    )


def check_and_initialize_monthly_cap_amounts(account: Account, start: date):
    # Check that current discount amounts for the account have a previous value, otherwise raise an exception
    caps = CAPDiscount.objects.filter(account=account).values_list("id", flat=True)
    previous_month = start - relativedelta(months=1)
    prev_cap_amounts = CAPDiscountAmount.objects.filter(
        cap_discount__in=caps, year=previous_month.year, month=previous_month.month
    )
    if prev_cap_amounts.count() != caps.count():
        raise MissingCAPAmountException(previous_month, account)

    # Initialize all discounts for this account
    for prev_cap_amount in prev_cap_amounts:
        initialize_cap_discount_amount(prev_cap_amount, start)


def initialize_cap_discount_amount(previous_amount: CAPDiscountAmount, start_date: date):
    cap_discount = previous_amount.cap_discount
    # Check if we need to reset the CAP
    start_for_rec = datetime(year=start_date.year, month=start_date.month, day=start_date.day)
    cap_reset = cap_discount.next_reset_date_after(start_date, inc=True)
    amount = Decimal(0)
    if start_for_rec == cap_reset:
        cap_discount.reset()
    # Only check previous amount if it's not a reset. Otherwise, it won't start over at 0
    elif previous_amount:
        amount = previous_amount.end
    discount_amount, created = CAPDiscountAmount.objects.get_or_create(
        cap_discount=cap_discount,
        year=start_date.year,
        month=start_date.month,
        defaults={"start": amount, "end": amount},
    )
    cap_discount.tmp_current_amount = discount_amount.start


def get_amounts_to_delete(account: Account, year, month) -> List[CAPDiscountAmount]:
    cap_amounts_to_delete: List[CAPDiscountAmount] = []
    # check to make sure they are all the latest invoices/amounts
    for cap_discount in CAPDiscount.objects.filter(account=account):
        latest_amount = cap_discount.latest_amount()
        if not latest_amount or not latest_amount.year == year or not latest_amount.month == month:
            raise NotLatestInvoiceException(latest_amount)
        cap_amounts_to_delete.append(latest_amount)
    return cap_amounts_to_delete


def delete_associated_amounts(account: Account, year, month, request):
    # delete associated CAP amounts for the year/month
    for cap_amount in get_amounts_to_delete(account, year, month):
        # If the amount was the first one, then delete the whole CAP discount
        if cap_amount.cap_discount.earliest_amount() == cap_amount:
            cap_amount.cap_discount.delete()
            messages.success(request, f"{cap_amount.cap_discount} was successfully deleted.", "data-speed=30000")
        else:
            cap_amount.delete()
            messages.success(request, f"{cap_amount} was successfully deleted.", "data-speed=30000")
