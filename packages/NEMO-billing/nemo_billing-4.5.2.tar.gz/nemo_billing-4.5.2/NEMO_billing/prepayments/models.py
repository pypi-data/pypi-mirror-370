from __future__ import annotations

import datetime
from _decimal import Decimal
from datetime import date
from logging import getLogger
from typing import Dict, List, Optional, Tuple

from NEMO.constants import CHAR_FIELD_MEDIUM_LENGTH, CHAR_FIELD_SMALL_LENGTH
from NEMO.models import (
    BaseCategory,
    BaseModel,
    EmailNotificationType,
    Project,
    User,
)
from NEMO.typing import QuerySetType
from NEMO.utilities import EmailCategory, get_month_timeframe, send_mail
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, validate_comma_separated_integer_list
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from NEMO_billing.customization import BillingCustomization
from NEMO_billing.invoices.customization import InvoiceCustomization
from NEMO_billing.invoices.models import BillableItemType, Invoice, InvoiceConfiguration, InvoiceSummaryItem
from NEMO_billing.invoices.processors import BillableItem
from NEMO_billing.invoices.utilities import display_amount
from NEMO_billing.models import CoreFacility
from NEMO_billing.prepayments.exceptions import (
    ProjectFundsExpiredException,
    ProjectFundsInactiveException,
    ProjectInsufficientFundsException,
)
from NEMO_billing.utilities import (
    Months,
    filter_date_year_month_gt,
    filter_date_year_month_lte,
    get_charges_amount_between,
    number_of_months_between_dates,
)


class ProjectPrepaymentDetail(BaseModel):
    project = models.OneToOneField(Project, verbose_name="Project", help_text="The project", on_delete=models.CASCADE)
    configuration = models.ForeignKey(InvoiceConfiguration, null=True, blank=True, on_delete=models.CASCADE)
    charge_types = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=CHAR_FIELD_SMALL_LENGTH,
        help_text="List of charge types allowed",
    )
    only_core_facilities = models.ManyToManyField(
        CoreFacility,
        blank=True,
        help_text="Limit which core facilities are allowed for this project. Leave blank to allow them all",
    )
    overdraft_amount_allowed = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="When set, this is the overdraft amount allowed for the project. Only works when there is at least one active fund with a positive balance.",
    )
    balance_last_updated = models.DateField(blank=True)

    @property
    def billable_charge_types(self) -> List[BillableItemType]:
        return [BillableItemType(int(value)) for value in self.charge_types.split(",") if value]

    def get_charge_types_display(self):
        return mark_safe(
            "<br>".join([charge_type.friendly_display_name() for charge_type in self.billable_charge_types])
        )

    def get_only_core_facilities_display(self):
        if not self.only_core_facilities.exists():
            return "All"
        return mark_safe("<br>".join([facility.name for facility in self.only_core_facilities.all()]))

    def active_funds(self, check_date: date, include_zero_balance=False) -> QuerySetType[Fund]:
        funds = self.fund_set.all()
        # Funds cannot all have expired
        non_expired_funds = funds.filter(
            Q(expiration_month__isnull=True, expiration_year__isnull=True)
            | filter_date_year_month_gt("expiration", check_date)
        )
        if not non_expired_funds.exists():
            raise ProjectFundsExpiredException(self.project)
        # At least one fund has to be active
        active_funds = non_expired_funds.filter(filter_date_year_month_lte("start", check_date))
        if not active_funds.exists():
            raise ProjectFundsInactiveException(self.project, check_date)
        if not include_zero_balance:
            active_funds = active_funds.filter(balance__gt=0)
        return active_funds.order_by("start_year", "start_month", "id")

    def update_balances_with_new_charges(self, new_charges: Decimal, as_of_date: date) -> List[Tuple[Fund, Decimal]]:
        fund_and_used_amount = []
        # This is used at the end of the month when invoicing
        active_funds_sorted_by_date = self.active_funds(as_of_date)
        last_item = active_funds_sorted_by_date.last()
        # Max out active funds one by one until the last one or no more charges
        for fund in active_funds_sorted_by_date:
            if new_charges <= 0:
                break
            if fund == last_item:
                # last fund, use all remaining charges
                update_amount = new_charges
            else:
                # max out other funds
                update_amount = min(fund.balance, new_charges)
            fund.update_balance(update_amount)
            fund_and_used_amount.append((fund, update_amount))
            new_charges = new_charges - update_amount
        self.balance_last_updated = as_of_date
        self.save()
        return fund_and_used_amount

    def get_prepayment_info(
        self, until: date, start_in_month: date = None, raise_exception=False
    ) -> (List[BillableItem], Decimal, Dict[int, Decimal]):
        # Returns total charges, total charges amount, and fund balances
        total_charges: List[BillableItem] = []
        total_charges_amount = Decimal(0)
        if not start_in_month:
            # balance is always one month behind
            start_in_month = (self.balance_last_updated + relativedelta(months=1)).replace(day=1)
        months = number_of_months_between_dates(until, start_in_month)
        # keep track of fund balances month to month
        fund_balances: Dict[int, Decimal] = {}
        for month in range(0, months + 1):
            month_date = start_in_month + relativedelta(months=month)
            # beginning and end of the month
            start, end = get_month_timeframe(month_date.isoformat())
            monthly_charges, monthly_charges_amount = get_charges_amount_between(
                self.project, self.configuration, start, end
            )
            total_charges.extend(monthly_charges)
            total_charges_amount = total_charges_amount + monthly_charges_amount
            if monthly_charges_amount:
                # only need to check funds valid at this date (expired or inactive won't be returned by active_funds)
                funds_left = Decimal(0)
                new_funds = Fund.objects.none()
                try:
                    new_funds = self.active_funds(end.date())
                except Exception:
                    if raise_exception:
                        raise
                last_fund_checked: Optional[Fund] = None
                last_item = new_funds.last()
                for fund in new_funds:
                    balance = max(fund_balances.setdefault(fund.id, fund.balance), Decimal(0))
                    if fund == last_item:
                        # last fund, use all remaining charges
                        update_amount = monthly_charges_amount
                    else:
                        # max out other funds
                        update_amount = min(fund.balance, monthly_charges_amount)
                    fund_balances[fund.id] = balance - update_amount
                    monthly_charges_amount = monthly_charges_amount - update_amount
                    funds_left += fund_balances[fund.id]
                    last_fund_checked = fund
                if last_fund_checked:
                    last_fund_checked.check_for_low_balance(funds_left)
                if (
                    not self.overdraft_amount_allowed
                    and not funds_left > 0
                    or self.overdraft_amount_allowed
                    and not funds_left + self.overdraft_amount_allowed > 0
                ):
                    if raise_exception:
                        raise ProjectInsufficientFundsException(self.project)
        total_charges.sort(key=lambda x: x.start)
        return total_charges, total_charges_amount, fund_balances

    def invoice_fund_summaries(self, invoice: Invoice) -> list[InvoiceSummaryItem]:
        fund_summaries = []
        fund_and_amounts = self.update_balances_with_new_charges(invoice.total_amount, invoice.end)
        for fund_and_amount in fund_and_amounts:
            fund, amount = fund_and_amount
            fund_summary = InvoiceSummaryItem(
                invoice=invoice, name=f"{fund} balance: {display_amount(fund.balance, invoice.configuration)}"
            )
            fund_summary.amount = -amount
            fund_summary.summary_item_type = InvoiceSummaryItem.InvoiceSummaryItemType.FUND
            # Set fund id in details, so we can find it later for voiding/deleting
            fund_summary.details = str(fund.id)
            fund_summaries.append(fund_summary)
        if InvoiceCustomization.get_bool("invoice_funds_show_total_balance"):
            # find all active funds, show total balance as type "other"
            # (otherwise it will break when trying to find fund by id)
            total_balance = Decimal(sum(fund.balance for fund in self.active_funds(invoice.end)))
            if total_balance > 0:
                total_balance_summary = InvoiceSummaryItem(
                    invoice=invoice,
                    name=f"Total funds remaining: {display_amount(total_balance, invoice.configuration)}",
                )
                total_balance_summary.amount = 0
                total_balance_summary.summary_item_type = InvoiceSummaryItem.InvoiceSummaryItemType.OTHER
                fund_summaries.append(total_balance_summary)
        return fund_summaries

    def restore_funds(self, invoice: Invoice, request):
        previous_balance_date = invoice.end - relativedelta(months=1)
        for fund_summary in invoice.invoicesummaryitem_set.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.FUND
        ):
            # Restore balance on each fund
            fund = Fund.objects.get(id=fund_summary.details)
            fund.update_balance(fund_summary.amount)
            messages.success(
                request,
                f"the balance for {fund} was successfully credited back {display_amount(-fund_summary.amount, invoice.configuration)}.",
                "data-speed=30000",
            )
        self.balance_last_updated = previous_balance_date
        self.save()

    def clean(self):
        if self.project_id:
            if not self.project.projectbillingdetails.no_tax and not self.configuration:
                raise ValidationError(
                    {
                        "configuration": _(
                            "Configuration is required for taxed projects. Select a configuration or make the project tax exempt"
                        )
                    }
                )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk and self.balance_last_updated is None:
            # Set original balance date to be last day of last month
            # Reusing get_month_timeframe since that's what will be used when running invoices
            self.balance_last_updated = get_month_timeframe(
                (datetime.date.today() - relativedelta(months=1)).isoformat()
            )[1]
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"Prepayment details for {self.project.name}"

    class Meta:
        ordering = ["project"]


class FundType(BaseCategory):
    pass


class Fund(BaseModel):
    project_prepayment = models.ForeignKey(ProjectPrepaymentDetail, on_delete=models.CASCADE)
    fund_type = models.ForeignKey(FundType, on_delete=models.PROTECT)
    reference = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH, null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=14)
    start_month = models.PositiveIntegerField(choices=Months.choices)
    start_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.MAXYEAR)],
    )
    expiration_month = models.PositiveIntegerField(null=True, blank=True, choices=Months.choices)
    expiration_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.MAXYEAR)],
    )
    balance = models.DecimalField(blank=True, decimal_places=2, max_digits=14)
    balance_warning_percent = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Send a warning email when the balance is below this percent.",
        validators=[MaxValueValidator(100)],
    )
    balance_warning_sent = models.DateTimeField(null=True, blank=True)
    note = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH, null=True, blank=True)

    @property
    def start_date(self) -> date:
        if self.start_year and self.start_month:
            return date(self.start_year, self.start_month, 1)

    @start_date.setter
    def start_date(self, value: date):
        if value:
            self.start_month, self.start_year = value.month, value.year
        else:
            self.start_month, self.start_year = None, None

    @property
    def expiration_date(self) -> date:
        if self.expiration_year and self.expiration_month:
            return date(self.expiration_year, self.expiration_month, 1)

    @expiration_date.setter
    def expiration_date(self, value: date):
        if value:
            self.expiration_month, self.expiration_year = value.month, value.year
        else:
            self.expiration_month, self.expiration_year = None, None

    def is_active(self, check_date: date):
        return self in self.project_prepayment.active_funds(check_date)

    def update_balance(self, new_charges: Decimal):
        self.balance = self.balance - new_charges
        self.save()

    def check_for_low_balance(self, balance_left: Decimal, raise_exception=False):
        try:
            if not self.balance_warning_sent:
                if self.balance_warning_percent:
                    warning_amount = self.balance_warning_percent / Decimal(100) * self.amount
                    if balance_left <= warning_amount:
                        subject = f"Low fund balance for project {self.project_prepayment.project.name}"
                        # Send to accounting staff, billing accounting email and project email
                        recipients = [
                            email
                            for user in User.objects.filter(is_active=True, is_accounting_officer=True)
                            for email in user.get_emails(EmailNotificationType.BOTH_EMAILS)
                        ]
                        billing_email = BillingCustomization.get("billing_accounting_email_address")
                        if billing_email:
                            recipients.append(billing_email)
                        recipients.extend(self.project_prepayment.project.projectbillingdetails.email_to())
                        message = "Hello,<br><br>\n\n"
                        message += f"You project {self.project_prepayment.project.name} has a low fund balance:<br>\n"
                        message += f"Original amount: {self.amount:.2f}<br>\n"
                        message += f"Current balance: {balance_left:.2f}<br>\n"
                        send_mail(
                            subject=subject,
                            content=message,
                            from_email=billing_email,
                            to=recipients,
                            email_category=EmailCategory.GENERAL,
                        )
                        self.balance_warning_sent = timezone.now()
                        self.save(update_fields=["balance_warning_sent"])
        except:
            getLogger(__name__).exception("Error checking/sending low balance email")
            if raise_exception:
                raise

    def clean(self):
        errors = {}
        if self.balance and self.balance > self.amount:
            errors["balance"] = _("The balance cannot be greater than the fund amount")
        if self.start_month and not self.start_year or self.start_year and not self.start_month:
            errors["start_year"] = "Both year/month are required together"
            errors["start_month"] = "Both year/month are required together"
        if self.expiration_month and not self.expiration_year or self.expiration_year and not self.expiration_month:
            errors["expiration_year"] = "Both year/month are required together"
            errors["expiration_month"] = "Both year/month are required together"
        if errors:
            raise ValidationError(errors)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk and self.balance is None:
            self.balance = self.amount
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        fund_name = f"Fund ref: {self.reference}" if self.reference else f"Fund #{self.id}"
        return f"{fund_name} ({self.fund_type})"
