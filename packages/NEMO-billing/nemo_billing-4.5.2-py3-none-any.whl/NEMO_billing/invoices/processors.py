import copy
import importlib
from collections import defaultdict
from copy import deepcopy
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from functools import partial
from typing import Dict, Iterable, List, Optional, Union

from NEMO.models import (
    Account,
    AreaAccessRecord,
    ConsumableWithdraw,
    Project,
    Reservation,
    StaffCharge,
    TrainingSession,
    UsageEvent,
    User,
)
from NEMO.utilities import format_daterange, format_datetime, get_month_timeframe
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.utils import get_deleted_objects
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest
from django.utils.timezone import localtime, make_aware, now

from NEMO_billing.invoices.customization import InvoiceCustomization
from NEMO_billing.invoices.exceptions import (
    InvoiceAlreadyExistException,
    InvoiceItemsNotInFacilityException,
    NoProjectCategorySetException,
    NoProjectDetailsSetException,
    NoRateSetException,
)
from NEMO_billing.invoices.models import (
    BillableItemType,
    Invoice,
    InvoiceConfiguration,
    InvoiceDetailItem,
    InvoiceSummaryItem,
    ProjectBillingDetails,
)
from NEMO_billing.invoices.utilities import display_amount, flatten, name_for_billable_item
from NEMO_billing.models import CoreFacility, CustomCharge
from NEMO_billing.rates.customization import BillingRatesCustomization
from NEMO_billing.rates.models import AreaHighestDailyRateGroup, Rate, RateType
from NEMO_billing.rates.utilities import get_rate_history
from NEMO_billing.templatetags.billing_tags import cap_discount_installed
from NEMO_billing.utilities import (
    get_billable_item_type_for_item,
    get_charges_amount_between,
    get_minutes_between_dates,
    round_decimal_amount,
)


# Helper class for invoices with separate detail items and summary items
class FullInvoice:
    def __init__(self, invoice: Invoice, details: List[InvoiceDetailItem], summaries: List[InvoiceSummaryItem]):
        self.invoice = invoice
        self.detail_items = details
        self.summary_items = summaries

    def save(self):
        if self.invoice:
            self.invoice.save_all(self.detail_items, self.summary_items)


class BillableItem(object):
    """Object representing a billable item (Tool usage, area access, consumable etc.)"""

    def __init__(self, item, project: Project, configuration: InvoiceConfiguration = None):
        self.item = item
        self.project: Optional[Project] = project
        self.configuration = configuration or InvoiceConfiguration()
        # Actual items
        self.tool = None
        self.area = None
        self.consumable = None
        # Rate (to be set later)
        self.rate: Optional[Rate] = None
        # Other properties
        self.start = getattr(item, "start", None) or getattr(item, "date", None)
        self.end = getattr(item, "end", None) or getattr(item, "date", None)
        self.user = getattr(item, "user", None) or getattr(item, "customer", None) or getattr(item, "trainee", None)
        self.validated: bool = getattr(item, "validated", False)
        self.validated_by: Optional[User] = getattr(item, "validated_by", None)
        self.waived: bool = getattr(item, "waived", False)
        self.waived_by: Optional[User] = getattr(item, "waived_by", None)
        self.waived_on: Optional[datetime] = getattr(item, "waived_on", None)
        self.proxy_user = (
            getattr(item, "operator", None)
            or getattr(item, "staff_member", None)
            or getattr(item, "creator", None)
            or getattr(item, "merchant", None)
            or getattr(item, "trainer", None)
            or getattr(getattr(item, "staff_charge", None), "staff_member", None)
        )
        # Setting tool, area, consumable and other properties
        self.item_type: Optional[BillableItemType] = None
        # Set quantity and amount if we know they cannot change later (Custom charge or supplies or training duration etc.)
        self.quantity: Optional[Decimal] = None
        self.amount: Optional[Decimal] = None
        self.core_facility: Optional[CoreFacility] = None
        self.rate_type: Optional[RateType] = None
        self.item_type = get_billable_item_type_for_item(item)
        if isinstance(item, UsageEvent):
            self.tool = item.tool
            self.rate_type = self.configuration.rates_types.get(RateType.Type.TOOL_USAGE)
        elif isinstance(item, AreaAccessRecord):
            self.area = item.area
            self.rate_type = self.configuration.rates_types.get(RateType.Type.AREA_USAGE)
        elif isinstance(item, StaffCharge):
            self.rate_type = self.configuration.rates_types.get(RateType.Type.STAFF_CHARGE)
            if not getattr(item, "core_facility", None):
                # We first check if there was an area access, in which case we will use the area's facility
                area_charge: AreaAccessRecord = AreaAccessRecord.objects.filter(staff_charge_id=item.id).first()
                if area_charge:
                    self.core_facility = area_charge.area.core_facility
                else:
                    # Otherwise, check for tool usage on behalf of the same customer during the time
                    tool_usage: UsageEvent = UsageEvent.objects.filter(
                        operator=item.staff_member, user=item.customer, start__gt=item.start, start__lte=item.end
                    ).first()
                    if tool_usage:
                        self.core_facility = tool_usage.tool.core_facility
        elif isinstance(item, Reservation):
            self.tool = item.tool
            self.area = item.area
            if self.tool:
                self.rate_type = self.configuration.rates_types.get(RateType.Type.TOOL_MISSED_RESERVATION)
            if self.area:
                self.rate_type = self.configuration.rates_types.get(RateType.Type.AREA_MISSED_RESERVATION)
        elif isinstance(item, CustomCharge):
            # Quantity and amount will never change so set them now
            self.quantity = 1
            self.amount = item.amount
        elif isinstance(item, TrainingSession):
            self.tool = item.tool
            # Training duration will never change
            self.quantity = item.duration
            if item.type == TrainingSession.Type.INDIVIDUAL:
                self.rate_type = self.configuration.rates_types.get(RateType.Type.TOOL_TRAINING_INDIVIDUAL)
            else:
                self.rate_type = self.configuration.rates_types.get(RateType.Type.TOOL_TRAINING_GROUP)
        elif isinstance(item, ConsumableWithdraw):
            self.consumable = item.consumable
            # Supply order quantity will never change
            self.quantity = item.quantity
            self.rate_type = self.configuration.rates_types.get(RateType.Type.CONSUMABLE)
        if not self.core_facility:
            self.core_facility = (
                getattr(item, "core_facility", None)
                or getattr(self.tool, "core_facility", None)
                or getattr(self.area, "core_facility", None)
                or getattr(self.consumable, "core_facility", None)
            )

    @property
    def name(self):
        return name_for_billable_item(self)

    @property
    def display_rate(self):
        return get_rate_with_currency(self.configuration, self.rate.display_rate()) if self.rate else None

    @property
    def display_amount(self):
        amount = display_amount(self.amount, self.configuration)
        return f"{amount}{' (waived)' if self.waived else ''}"

    @property
    def rate_time_name_add(self):
        return f" - {self.rate.time.name}" if self.rate and self.rate.time else ""

    @property
    def display_quantity(self):
        if self.item_type in [
            BillableItemType.CONSUMABLE,
            BillableItemType.CUSTOM_CHARGE,
            BillableItemType.MISSED_RESERVATION,
        ]:
            return self.quantity
        else:
            return timedelta(seconds=round(self.quantity * 60))

    def calculate_amount(self, rate: Rate, new_start, new_end, copy_original=True):
        new_billable = deepcopy(self) if copy_original else self
        new_billable.rate = rate
        new_billable.start = new_start
        new_billable.end = new_end
        # Calculate quantity only if it wasn't already set
        if not new_billable.quantity:
            new_billable.quantity = get_minutes_between_dates(new_billable.start, new_billable.end)
        # Calculate amount only if not already set
        if not new_billable.amount:
            new_billable.amount = rate.calculate_amount(new_billable.quantity)
        return new_billable


def find_billable_rates(billable_item: BillableItem, configuration: InvoiceConfiguration) -> List[Rate]:
    return find_rates(
        billable_item.rate_type,
        billable_item.project,
        configuration,
        localtime(billable_item.end).date(),
        billable_item.tool,
        billable_item.area,
        billable_item.consumable,
    )


def find_rates(
    rate_type: RateType,
    project: Project,
    config: InvoiceConfiguration,
    as_of_date: date,
    tool=None,
    area=None,
    consumable=None,
) -> List[Rate]:
    category = None
    tool_id = None
    area_id = None
    consumable_id = None
    try:
        project.projectbillingdetails
    except (ProjectBillingDetails.DoesNotExist, AttributeError):
        # Attribute error just in case we don't have a project, which should never happen
        raise NoProjectDetailsSetException(project)
    if rate_type.category_specific:
        if config.rates_exist and not project.projectbillingdetails.category:
            raise NoProjectCategorySetException(rate_type, project)
        category = project.projectbillingdetails.category
    if rate_type.item_specific:
        if tool:
            tool_id = tool.id
        elif area:
            area_id = area.id
        elif consumable:
            consumable_id = consumable.id
    category_id = category.id if category else None
    matching_rates = get_rate_history(
        rate_type.id, config.all_rates, category_id, tool_id, area_id, consumable_id, as_of_date
    ).current_rate()
    base_rate = matching_rates.get(None, None)
    if not rate_type.can_have_rate_time():
        # We can only have one rate
        if base_rate:
            return [base_rate]
        else:
            raise NoRateSetException(rate_type, category, tool=tool, area=area, consumable=consumable)
    else:
        # We need at least one rate, and one of them being a base rate (without time)
        if not matching_rates or not base_rate:
            raise NoRateSetException(rate_type, category, tool=tool, area=area, consumable=consumable)
        return list(matching_rates.values())


def get_rate_with_currency(config: InvoiceConfiguration, rate: str):
    return f"{config.currency} {rate}" if config.currency else rate


class InvoiceDataProcessor(object):
    # Do all this in a transaction so everything gets rolled back if an error happened
    @transaction.atomic
    def generate_invoice_for_account(self, month, account, configuration, user, raise_if_exists=False) -> List[Invoice]:
        full_invoice_list = []
        if not InvoiceCustomization.get_bool("invoice_skip_inactive_accounts") or account.active:
            # Start and end will be included in the results. So for example for September data, use: 09/01 12am to 09/30 11:59:99
            start, end = get_month_timeframe(month)
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
                    full_invoice_list.append(invoice)
            for full_invoice in full_invoice_list:
                full_invoice.save()
        return [full_invoice.invoice for full_invoice in full_invoice_list]

    def generate_invoice(
        self,
        start: datetime,
        end: datetime,
        project: Project,
        configuration: InvoiceConfiguration,
        user: User,
        billables: List[BillableItem],
        raise_if_exists=False,
    ) -> FullInvoice:
        try:
            project_details = ProjectBillingDetails.objects.get(project_id=project.id)
        except ProjectBillingDetails.DoesNotExist:
            raise NoProjectDetailsSetException(project)
        # If there is already an invoice for this project for those dates, don't regenerate it (unless void).
        existing_invoices = Invoice.objects.filter(
            start=start, end=end, project_details=project_details, voided_date=None
        )
        if existing_invoices.exists():
            if raise_if_exists:
                raise InvoiceAlreadyExistException(existing_invoices.first())
        # No existing invoices, continue
        elif not project_details.no_charge:
            # Project can be charged, so proceed
            return invoice_data_processor_class.process_data(
                start, end, project_details, configuration, user, billables
            )

    def process_data(
        self,
        start: datetime,
        end: datetime,
        project_details: ProjectBillingDetails,
        configuration: InvoiceConfiguration,
        user: User,
        billables: List[BillableItem],
    ) -> Optional[FullInvoice]:
        invoice = self.create_invoice(start, end, project_details, configuration, user)
        detail_items: List[InvoiceDetailItem] = list(
            map(partial(billable_to_invoice_detail_item, invoice=invoice), billables)
        )
        if settings.INVOICE_ALL_ITEMS_MUST_BE_IN_FACILITY:
            for detail_item in detail_items:
                if not detail_item.core_facility:
                    raise InvoiceItemsNotInFacilityException(detail_item)
        if detail_items:
            summary_items = self.get_invoice_summary_items(invoice, detail_items)
            return FullInvoice(invoice, detail_items, summary_items)

    def get_billable_items(
        self,
        start: datetime,
        end: datetime,
        config: InvoiceConfiguration,
        customer_filter=Q(),
        user_filter=Q(),
        trainee_filter=Q(),
        raise_no_rate=True,
    ) -> List[BillableItem]:
        items: List[BillableItem] = []
        config.init_rate_help()
        items.extend(self._area_access_records(start, end, config, customer_filter, raise_no_rate))
        items.extend(self._consumable_withdrawals(start, end, config, customer_filter, raise_no_rate))
        items.extend(self._missed_reservations(start, end, config, user_filter, raise_no_rate))
        items.extend(self._staff_charges(start, end, config, customer_filter, raise_no_rate))
        items.extend(self._training_sessions(start, end, config, trainee_filter, raise_no_rate))
        items.extend(self._tool_usages(start, end, config, user_filter, raise_no_rate))
        items.extend(self._custom_charges(start, end, config, customer_filter, raise_no_rate))
        self.process_daily_rates(items)
        return items

    def get_billable_items_with_charge_filters(
        self,
        start: datetime,
        end: datetime,
        config: InvoiceConfiguration,
        usage_filter,
        area_access_filter,
        staff_charges_filter,
        consumable_filter,
        reservation_filter,
        training_filter,
        custom_charges_filter,
        raise_no_rate=True,
    ) -> List[BillableItem]:
        items: List[BillableItem] = []
        config.init_rate_help()
        items.extend(self._area_access_records(start, end, config, area_access_filter, raise_no_rate))
        items.extend(self._consumable_withdrawals(start, end, config, consumable_filter, raise_no_rate))
        items.extend(self._missed_reservations(start, end, config, reservation_filter, raise_no_rate))
        items.extend(self._staff_charges(start, end, config, staff_charges_filter, raise_no_rate))
        items.extend(self._training_sessions(start, end, config, training_filter, raise_no_rate))
        items.extend(self._tool_usages(start, end, config, usage_filter, raise_no_rate))
        items.extend(self._custom_charges(start, end, config, custom_charges_filter, raise_no_rate))
        self.process_daily_rates(items)
        return items

    def process_daily_rates(self, items: List[BillableItem]):
        # This function will grab all the charges that have a daily rate and organize them by rate_id
        # Then go over all items with the same rate and keep track of which ones we've processed for each day
        # If we already processed one on the same day, set the following ones to 0
        daily_by_account = cap_discount_installed() and BillingRatesCustomization.get_bool("rates_daily_per_account")
        daily_rate_charges = defaultdict(list)
        for item in copy.copy(items):
            if not item.waived and item.rate and item.rate.daily and item.rate.daily_split_multi_day_charges:
                # we need to split multi day charges
                # to simplify things, we are deciding here to use the end date of the original charge as reference point
                # this means that if a charge spans 7 days, all 7 day charges will be added to the invoice that
                # includes the last day. They will not be added to previous invoices.
                items.extend(split_records_by_day(item))
                items.remove(item)
        for item in items:
            if not item.waived and item.rate and item.rate.daily:
                daily_rate_charges[str(item.rate.id)].append(item)
        group_area_charges_by_day: Dict[str, List[BillableItem]] = defaultdict(list)
        for daily_charges in daily_rate_charges.values():
            treated_day: Dict[str, List[datetime.date]] = defaultdict(list)
            for item in daily_charges:
                # prefixes here (a, p, u, g) are not exactly necessary but help with debugging to know the model type
                account_id_or_project_id = f"a{item.project.account.id}" if daily_by_account else f"p{item.project.id}"
                key = f"u{item.user.id}-{account_id_or_project_id}"
                # if the end is at midnight, it should count for the previous day, so let's subtract a microsecond to get that day
                # this will only have a real effect if it ends right at midnight, so it should be safe
                day: datetime.date = (item.end - timedelta(microseconds=1)).astimezone().date()
                # set up a list of daily area charges that are part of a group for later processing
                if item.item_type == BillableItemType.AREA_ACCESS:
                    area_group = AreaHighestDailyRateGroup.objects.filter(areas__in=[item.area]).first()
                    if area_group:
                        group_area_day_key = f"{key}-g{area_group.id}-d{day.strftime('%Y%m%d')}"
                        group_area_charges_by_day[group_area_day_key].append(item)
                if day in treated_day[key]:
                    # If we have already processed this day for this rate, set to 0
                    item.amount = 0
                else:
                    treated_day[key].append(day)
        # let's do a second pass to deal with zeroing out daily charges in the same group
        for group_area_daily_charges in group_area_charges_by_day.values():
            # first, sort grouped areas by most expensive (all daily rates at this point)
            sorted_group_area_daily_charges = sorted(group_area_daily_charges, key=lambda x: -x.rate.amount)
            for order, group_area_item in enumerate(sorted_group_area_daily_charges):
                # the first one is the most expensive, we can zero out all other ones
                if order != 0:
                    group_area_item.amount = 0

    def create_invoice(self, start, end, project_details, configuration, user: User) -> Invoice:
        invoice = Invoice()
        invoice.start = start
        invoice.end = end
        invoice.project_details = project_details
        invoice.configuration = configuration
        invoice.created_by = user
        invoice.total_amount = 0
        return invoice

    @transaction.atomic
    def void_invoice(self, invoice: Invoice, request: HttpRequest):
        # NOTE: we are voiding all invoices for this account,
        # in case daily rates were applied across projects of the same account
        invoice_account = invoice.project_details.project.account
        invoice_year, invoice_month = invoice.start.year, invoice.start.month
        for invoice in get_account_invoices(invoice_account, invoice_year, invoice_month):
            self.do_void_invoice(invoice, request)

    def do_void_invoice(self, invoice: Invoice, request: HttpRequest):
        if not invoice.voided_date:
            if hasattr(invoice.project_details.project, "projectprepaymentdetail"):
                invoice.project_details.project.projectprepaymentdetail.restore_funds(invoice, request)
            invoice.voided_date = now()
            invoice.voided_by = request.user
            invoice.save()
            messages.success(
                request, f"Invoice {invoice.invoice_number} was successfully marked as void.", "data-speed=30000"
            )

    @transaction.atomic
    def delete_invoice(self, invoice: Invoice, request: HttpRequest):
        # NOTE: we are deleting all invoices for this account,
        # in case daily rates were applied across projects of the same account
        invoice_account = invoice.project_details.project.account
        invoice_year, invoice_month = invoice.start.year, invoice.start.month
        invoices_to_delete: List[Invoice] = get_account_invoices(invoice_account, invoice_year, invoice_month)
        for invoice in invoices_to_delete:
            self.do_delete_invoice(invoice, request)

    def do_delete_invoice(self, invoice: Invoice, request: HttpRequest):
        if hasattr(invoice.project_details.project, "projectprepaymentdetail"):
            invoice.project_details.project.projectprepaymentdetail.restore_funds(invoice, request)
        invoice.delete()
        messages.success(request, f"Invoice {invoice.invoice_number} was successfully deleted.", "data-speed=30000")

    def get_deleted_objects(self, invoices: Iterable[Invoice], request: HttpRequest, admin_site):
        # gather all related objects to delete: other invoices, cap discounts, cap discount amounts
        related_invoices = []
        for invoice in invoices:
            invoice_account = invoice.project_details.project.account
            invoice_year, invoice_month = invoice.start.year, invoice.start.month
            related_invoices.extend(get_account_invoices(invoice_account, invoice_year, invoice_month))
        invoice_deleted_objects = get_deleted_objects(related_invoices, request, admin_site)
        return (
            invoice_deleted_objects[0],
            {**invoice_deleted_objects[1]},
            invoice_deleted_objects[2],
            invoice_deleted_objects[2],
        )

    def _tool_usages(self, start, end, config, x_filter=Q(), raise_no_rate=True) -> List[BillableItem]:
        usage_events = UsageEvent.objects.filter(end__gte=start, end__lte=end).prefetch_related(
            "user",
            "operator",
            "waived_by",
            "tool",
            "tool__core_rel__core_facility",
            "project",
            "project__account",
            "project__projectbillingdetails__category",
            "project__projectbillingdetails__institution__institution_type",
            "project__projectbillingdetails__department",
        )
        usage_events = usage_events.filter(x_filter).order_by("start")
        return flatten([process_billables(u, u.project, config, raise_no_rate) for u in usage_events])

    def _area_access_records(self, start, end, config, x_filter=Q(), raise_no_rate=True) -> List[BillableItem]:
        access_records = AreaAccessRecord.objects.filter(end__gte=start, end__lte=end).prefetch_related(
            "project__account",
            "project__projectbillingdetails__category",
            "project__projectbillingdetails__institution__institution_type",
            "project__projectbillingdetails__department",
            "customer",
            "staff_charge__staff_member",
            "waived_by",
            "area",
            "area__core_rel__core_facility",
        )
        access_records = access_records.filter(x_filter).order_by("start")
        return flatten([process_billables(access, access.project, config, raise_no_rate) for access in access_records])

    def _missed_reservations(self, start, end, config, x_filter=Q(), raise_no_rate=True) -> List[BillableItem]:
        missed_res = Reservation.objects.filter(missed=True, end__gte=start, end__lte=end).prefetch_related(
            "user",
            "waived_by",
            "project",
            "project__account",
            "project__projectbillingdetails__category",
            "project__projectbillingdetails__institution__institution_type",
            "project__projectbillingdetails__department",
            "tool",
            "tool__core_rel__core_facility",
            "area",
            "area__core_rel__core_facility",
        )
        missed_res = missed_res.filter(x_filter).order_by("start")
        return flatten([process_billables(missed, missed.project, config, raise_no_rate) for missed in missed_res])

    def _staff_charges(self, start, end, config, x_filter=Q(), raise_no_rate=True) -> List[BillableItem]:
        staff_charges = StaffCharge.objects.filter(end__gte=start, end__lte=end).prefetch_related(
            "project",
            "project__account",
            "project__projectbillingdetails__category",
            "project__projectbillingdetails__institution__institution_type",
            "project__projectbillingdetails__department",
            "customer",
            "waived_by",
            "staff_member",
            "core_rel__core_facility",
        )
        staff_charges = staff_charges.filter(x_filter).order_by("start")
        return flatten([process_billables(c, c.project, config, raise_no_rate) for c in staff_charges])

    def _consumable_withdrawals(self, start, end, config, x_filter=Q(), raise_no_rate=True) -> List[BillableItem]:
        withdrawals = ConsumableWithdraw.objects.filter(date__gte=start, date__lte=end).prefetch_related(
            "project",
            "project__account",
            "project__projectbillingdetails__category",
            "project__projectbillingdetails__institution__institution_type",
            "project__projectbillingdetails__department",
            "customer",
            "merchant",
            "waived_by",
            "consumable",
            "consumable__core_rel__core_facility",
        )
        withdrawals = withdrawals.filter(x_filter).order_by("date")
        return flatten([process_billables(w, w.project, config, raise_no_rate) for w in withdrawals])

    def _training_sessions(self, start, end, config, x_filter=Q(), raise_no_rate=True) -> List[BillableItem]:
        training_sessions = TrainingSession.objects.filter(date__gte=start, date__lte=end).prefetch_related(
            "trainee",
            "trainer",
            "waived_by",
            "tool",
            "tool__core_rel__core_facility",
            "project",
            "project__account",
            "project__projectbillingdetails__category",
            "project__projectbillingdetails__institution__institution_type",
            "project__projectbillingdetails__department",
        )
        training_sessions = training_sessions.filter(x_filter).order_by("date")
        return flatten([process_billables(t, t.project, config, raise_no_rate) for t in training_sessions])

    def _custom_charges(self, start, end, config, x_filter=Q(), raise_no_rate=True) -> List[BillableItem]:
        custom_charges = CustomCharge.objects.filter(date__gte=start, date__lte=end).prefetch_related(
            "project",
            "project__account",
            "project__projectbillingdetails__category",
            "project__projectbillingdetails__institution__institution_type",
            "project__projectbillingdetails__department",
            "customer",
            "waived_by",
            "core_facility",
        )
        custom_charges = custom_charges.filter(x_filter).order_by("date")
        return flatten([process_billables(cc, cc.project, config, raise_no_rate) for cc in custom_charges])

    def get_invoice_summary_items(self, invoice, detail_items: List[InvoiceDetailItem]) -> List[InvoiceSummaryItem]:
        summaries: List[InvoiceSummaryItem] = []
        # Core facilities sorted alphabetically by non-empty ones first
        for core_facility in invoice.sorted_core_facilities(detail_items):
            details = [item for item in detail_items if item.core_facility == core_facility]
            summaries.extend(self.get_summary_items_for_facility(invoice, core_facility, details))

        # Recap of all charges
        charges_amount = sum(
            [
                summary.amount
                for summary in summaries
                if summary.summary_item_type == InvoiceSummaryItem.InvoiceSummaryItemType.SUBTOTAL
            ]
        )

        # Tax
        tax_amount = Decimal(0)
        if invoice.configuration.tax and charges_amount > Decimal(0) and not invoice.project_details.no_tax:
            tax = InvoiceSummaryItem(
                invoice=invoice, name=f"{invoice.configuration.tax_name} ({invoice.configuration.tax_display()}%)"
            )
            tax.summary_item_type = InvoiceSummaryItem.InvoiceSummaryItemType.TAX
            tax_amount = round_decimal_amount(charges_amount * invoice.configuration.tax_amount())
            tax.amount = tax_amount
            summaries.append(tax)

        invoice.total_amount = charges_amount + tax_amount

        if hasattr(invoice.project_details.project, "projectprepaymentdetail"):
            prepayment = invoice.project_details.project.projectprepaymentdetail
            fund_summaries = prepayment.invoice_fund_summaries(invoice)
            total_fund_used = Decimal(0)
            for fund_summary in fund_summaries:
                summaries.append(fund_summary)
                total_fund_used += fund_summary.amount
            invoice.total_amount = invoice.total_amount + total_fund_used
        if InvoiceCustomization.get_bool("invoice_show_hard_cap_status"):
            hard_caps = (
                invoice.project_details.project.projectbillinghardcap_set.filter(enabled=True)
                .exclude(start_date__lt=invoice.start, end_date__lt=invoice.start)
                .exclude(start_date__gt=invoice.end, end_date__gt=invoice.end)
            )
            for hard_cap in hard_caps:
                start_datetime = make_aware(datetime.combine(hard_cap.start_date or date.min, time.min))
                end_datetime = make_aware(datetime.combine(hard_cap.end_date or date.max, time.max))
                date_range_display = ""
                if hard_cap.start_date and hard_cap.end_date:
                    date_range_display = f" during the period {format_daterange(hard_cap.start_date, hard_cap.end_date, d_format='SHORT_DATE_FORMAT')}"
                elif hard_cap.start_date:
                    date_range_display = f" since {format_datetime(hard_cap.start_date, df='SHORT_DATE_FORMAT')}"
                elif hard_cap.end_date:
                    date_range_display = f" until {format_datetime(hard_cap.end_date, df='SHORT_DATE_FORMAT')}"
                charges, amount = get_charges_amount_between(
                    hard_cap.project,
                    hard_cap.configuration,
                    start_datetime,
                    end_datetime,
                    hard_cap.billable_charge_types,
                )
                hard_cap_summary = InvoiceSummaryItem(
                    invoice=invoice,
                    name=f"CAP - You have used: {display_amount(amount, invoice.configuration)} of {display_amount(hard_cap.amount, invoice.configuration)} available{date_range_display}",
                )
                # hard_cap_summary.amount = 0
                hard_cap_summary.summary_item_type = InvoiceSummaryItem.InvoiceSummaryItemType.OTHER
                summaries.append(hard_cap_summary)
        return summaries

    def get_summary_items_for_facility(self, invoice: Invoice, core_facility: str, details) -> List[InvoiceSummaryItem]:
        facility_summaries: List[InvoiceSummaryItem] = []
        for billable_type in BillableItemType:
            items = [item for item in details if item.item_type == billable_type.value]
            facility_summaries.extend(self.get_recap_usage_summary(invoice, core_facility, items))

        facility_subtotal = InvoiceSummaryItem(invoice=invoice, name="Subtotal", core_facility=core_facility)
        facility_subtotal.summary_item_type = InvoiceSummaryItem.InvoiceSummaryItemType.SUBTOTAL
        facility_subtotal.amount = round_decimal_amount(sum(item.amount for item in details if not item.waived))
        facility_summaries.append(facility_subtotal)

        return facility_summaries

    def get_recap_usage_summary(self, invoice, facility, items: List[InvoiceDetailItem]) -> List[InvoiceSummaryItem]:
        summary_items: List[InvoiceSummaryItem] = []
        if items:
            item_type_value = items[0].item_type
            item_names = list({item.name for item in items})
            item_names.sort()
            for item_name in item_names:
                item_with_name_list = [item for item in items if item.name == item_name]
                non_waived_items = [item for item in item_with_name_list if not item.waived]
                item_rate = item_with_name_list[0].rate
                total_q = sum(item.quantity for item in non_waived_items)
                if BillableItemType(item_type_value).is_time_type():
                    quantity_display = f" ({total_q/60:.2f} hours)"
                elif item_type_value == BillableItemType.CUSTOM_CHARGE.value:
                    quantity_display = ""
                else:
                    quantity_display = f" (x {total_q})"
                summary_item_name = f"{item_name}{quantity_display}"
                summary_item = InvoiceSummaryItem(invoice=invoice, name=summary_item_name, core_facility=facility)
                summary_item.summary_item_type = InvoiceSummaryItem.InvoiceSummaryItemType.ITEM
                summary_item.item_type = item_type_value
                summary_item.details = item_rate
                summary_item.amount = round_decimal_amount(sum(item.amount for item in non_waived_items))
                summary_items.append(summary_item)
        return summary_items

    def category_name_for_item_type(self, item_type: Optional[Union[BillableItemType, int]]) -> str:
        billable_item_type = (
            item_type
            if isinstance(item_type, BillableItemType)
            else BillableItemType(item_type) if isinstance(item_type, int) else None
        )
        if not billable_item_type:
            return ""
        if billable_item_type == BillableItemType.TOOL_USAGE:
            return "Tool Usage"
        elif billable_item_type == BillableItemType.AREA_ACCESS:
            return "Area Access"
        elif billable_item_type == BillableItemType.CONSUMABLE:
            return "Supplies/Materials"
        elif billable_item_type == BillableItemType.STAFF_CHARGE:
            return "Technical Work"
        elif billable_item_type == BillableItemType.TRAINING:
            return "Training"
        elif billable_item_type == BillableItemType.MISSED_RESERVATION:
            return "Missed Reservations"
        elif billable_item_type == BillableItemType.CUSTOM_CHARGE:
            return "Other"

    def name_for_item(self, billable_item: BillableItem) -> str:
        name = (
            getattr(billable_item.tool, "name", None)
            or getattr(billable_item.area, "name", None)
            or getattr(billable_item.consumable, "name", None)
            or getattr(billable_item.item, "name", None)
        )
        if isinstance(billable_item.item, TrainingSession):
            name = f"{billable_item.tool.name} ({billable_item.item.get_type_display()})"
        if not name and isinstance(billable_item.item, StaffCharge):
            name = "Staff time"
        return f"{name}{billable_item.rate_time_name_add}"


def billable_to_invoice_detail_item(item: BillableItem, invoice: Optional[Invoice]) -> InvoiceDetailItem:
    invoice_item = InvoiceDetailItem(invoice=invoice)
    invoice_item.content_object = item.item
    invoice_item.quantity = item.quantity
    invoice_item.start = item.start
    invoice_item.end = item.end
    invoice_item.user = item.user.username if item.user else None
    invoice_item.amount = item.amount
    invoice_item.rate = item.display_rate
    invoice_item.core_facility = item.core_facility.name if item.core_facility else None
    invoice_item.item_type = item.item_type.value
    invoice_item.name = item.name
    invoice_item.waived = item.waived
    return invoice_item


def process_billables(item, project, configuration: InvoiceConfiguration, raise_no_rate=True) -> List[BillableItem]:
    billable = BillableItem(item, project, configuration)
    try:
        # Only proceed if we don't have an amount already
        if not billable.amount:
            # Otherwise, find the rates and calculate the amount
            rates = find_billable_rates(billable, configuration)
            billables: List[BillableItem] = []
            break_up_and_add(billables, rates, billable.start, billable.end, billable)
            return billables
    except (NoRateSetException, NoProjectCategorySetException, NoProjectDetailsSetException):
        if raise_no_rate:
            raise
    # If we already have an amount, or if there is an error & we don't raise it, return the original billable
    return [billable]


def break_up_and_add(
    billables: List[BillableItem], rates: List[Rate], start_time: datetime, end_time: datetime, original_billable
):
    # This function will break the date range into chunks of BillableItems if there are multiple rates that apply
    # 1. Find the earliest rate that applies to this date range as well as its start time and end time.
    # 2. The new start is the one given by the first_rate_that_applies method (max of rate start time and original start time)
    # 3. If the new start is later than the start, that means we have a gap and need to apply the base rate to the in between times
    # 4. The new end is the min of rate start time + rate duration and the original end
    # 5. Apply it to a new BillableItem and calculate the new amount.
    # 6. Call recursively on the rest of the date range (new end until original end)
    # 7. Recursion ends when we don't have a rate with time that applies (set base rate and done)
    # use UTC to avoid issues with DST
    start_utc, end_utc = (
        start_time.astimezone(timezone.utc),
        end_time.astimezone(timezone.utc),
    )
    rate, new_start_utc, new_end_utc = earliest_rate_match(rates, start_utc, end_utc)
    base_rate = next(r for r in rates if not r.time)
    if not rate:
        billables.append(original_billable.calculate_amount(base_rate, start_utc, end_utc, copy_original=False))
    else:
        # If the new start is later than the current start, we have a "hole" between timed rates, so apply the original base rate
        if new_start_utc > start_utc:
            billables.append(original_billable.calculate_amount(base_rate, start_utc, new_start_utc))
        billables.append(original_billable.calculate_amount(rate, new_start_utc, new_end_utc))
        # keep going until we reach the end
        if new_end_utc != end_time:
            break_up_and_add(billables, rates, new_end_utc, end_time, original_billable)


def earliest_rate_match(rates: List[Rate], start_time: datetime, end_time: datetime) -> (Rate, datetime, datetime):
    new_rate, new_start, new_end = None, None, None
    for rate in rates:
        # We only care about rate with times, since they are the only ones that can override the base rate
        if rate.time:
            tmp_start, tmp_end = rate.time.earliest_match(start_time, end_time)
            if tmp_start and (not new_start or tmp_start < new_start):
                new_start = tmp_start
                new_end = tmp_end
                new_rate = rate
    return new_rate, new_start, new_end


def split_records_by_day(item: BillableItem) -> List[BillableItem]:
    split_records = []
    curr_start = localtime(item.start)

    while curr_start < item.end:
        potential_end = min(make_aware(datetime.combine(curr_start.date(), time.min) + timedelta(days=1)), item.end)
        if potential_end < item.end:
            curr_end = potential_end
        else:
            curr_end = item.end
        # Create a new record if dates are different
        if curr_end != item.end or curr_start != item.start:
            new_record = deepcopy(item)
            new_record.start = curr_start
            new_record.end = curr_end
            new_record.quantity = get_minutes_between_dates(new_record.start, new_record.end)
            split_records.append(new_record)
        else:
            split_records.append(item)

        curr_start = curr_end
    return split_records


def get_account_invoices(account: Account, year: int, month: int) -> List[Invoice]:
    return Invoice.objects.filter(start__year=year, start__month=month, project_details__project__account=account)


def get_invoice_data_processor_class() -> InvoiceDataProcessor:
    processor_class = getattr(
        settings, "INVOICE_DATA_PROCESSOR_CLASS", "NEMO_billing.invoices.processors.InvoiceDataProcessor"
    )
    assert isinstance(processor_class, str)
    pkg, attr = processor_class.rsplit(".", 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret()


invoice_data_processor_class = get_invoice_data_processor_class()
