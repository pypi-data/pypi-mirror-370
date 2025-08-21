import datetime
import decimal
import math
from typing import List, Union

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.forms import BaseForm, HiddenInput


class Months(models.IntegerChoices):
    JAN = 1, "JANUARY"
    FEB = 2, "FEBRUARY"
    MAR = 3, "MARCH"
    APR = 4, "APRIL"
    MAY = 5, "MAY"
    JUN = 6, "JUNE"
    JUL = 7, "JULY"
    AUG = 8, "AUGUST"
    SEP = 9, "SEPTEMBER"
    OCT = 10, "OCTOBER"
    NOV = 11, "NOVEMBER"
    DEC = 12, "DECEMBER"


class IntMultipleChoiceField(forms.MultipleChoiceField):
    def prepare_value(self, value):
        if value is None:
            return value
        if type(value) is list:
            return [int(val) for val in value]
        return value.split(",")

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages["invalid_list"], code="invalid_list")
        return ",".join([str(val) for val in value])

    def validate(self, value):
        """Validate that the input is a list or tuple."""
        if self.required and not value:
            raise ValidationError(self.error_messages["required"], code="required")
        # Validate that each value in the value list is in self.choices.
        for val in value.split(","):
            if not self.valid_value(val):
                raise ValidationError(
                    self.error_messages["invalid_choice"],
                    code="invalid_choice",
                    params={"value": val},
                )


def disable_form_field(form: BaseForm, field_name):
    if field_name in form.fields:
        form.fields[field_name].disabled = True
        form.fields[field_name].required = False


def hide_form_field(form: BaseForm, field_name):
    if field_name in form.fields:
        disable_form_field(form, field_name)
        form.fields[field_name].widget = HiddenInput()


# Utility functions to compare dates that are stored in month/year format
def filter_date_year_month_gte(field_name: str, date_to_compare: datetime.date) -> Q:
    return Q(**{f"{field_name}_year__gt": date_to_compare.year}) | Q(
        **{f"{field_name}_year": date_to_compare.year, f"{field_name}_month__gte": date_to_compare.month}
    )


def filter_date_year_month_gt(field_name: str, date_to_compare: datetime.date) -> Q:
    return Q(**{f"{field_name}_year__gt": date_to_compare.year}) | Q(
        **{f"{field_name}_year": date_to_compare.year, f"{field_name}_month__gt": date_to_compare.month}
    )


def filter_date_year_month_lt(field_name: str, date_to_compare: datetime.date) -> Q:
    return Q(**{f"{field_name}_year__lt": date_to_compare.year}) | Q(
        **{f"{field_name}_year": date_to_compare.year, f"{field_name}_month__lt": date_to_compare.month}
    )


def filter_date_year_month_lte(field_name: str, date_to_compare: datetime.date) -> Q:
    return Q(**{f"{field_name}_year__lt": date_to_compare.year}) | Q(
        **{f"{field_name}_year": date_to_compare.year, f"{field_name}_month__lte": date_to_compare.month}
    )


def number_of_months_between_dates(end_date, start_date):
    return (end_date.year - start_date.year) * 12 + end_date.month - start_date.month


def get_charges_amount_between(
    project, configuration, start_date: datetime, end_date: datetime, charge_types: List = None
) -> (List, decimal.Decimal):
    from NEMO_billing.invoices.processors import invoice_data_processor_class as data_processor
    from NEMO_billing.invoices.models import InvoiceConfiguration

    project_filter = Q(project_id=project.id)
    config = configuration or InvoiceConfiguration.first_or_default()
    charges = data_processor.get_billable_items(
        start_date, end_date, config, project_filter, project_filter, project_filter
    )
    if charge_types:
        charges = [charge for charge in charges if charge.item_type in charge_types]
    total = sum(charge.amount for charge in charges if not charge.waived)
    if not project.projectbillingdetails.no_tax:
        taxes = total * config.tax_amount()
        total = total + taxes
    return charges, total


# Return the billable item type for a charge
def get_billable_item_type_for_item(item):
    from NEMO.models import UsageEvent, AreaAccessRecord, StaffCharge, Reservation, TrainingSession, ConsumableWithdraw
    from NEMO_billing.models import CustomCharge
    from NEMO_billing.invoices.models import BillableItemType

    if isinstance(item, UsageEvent):
        # Usage event by staff on behalf of user is considered staff charge
        return (
            BillableItemType.STAFF_CHARGE
            if item.remote_work and settings.STAFF_TOOL_USAGE_AS_STAFF_CHARGE
            else BillableItemType.TOOL_USAGE
        )
    elif isinstance(item, AreaAccessRecord):
        # Area access during staff charge is considered staff charge
        return (
            BillableItemType.STAFF_CHARGE
            if item.staff_charge and settings.STAFF_AREA_ACCESS_AS_STAFF_CHARGE
            else BillableItemType.AREA_ACCESS
        )
    elif isinstance(item, StaffCharge):
        return BillableItemType.STAFF_CHARGE
    elif isinstance(item, Reservation):
        return BillableItemType.MISSED_RESERVATION
    elif isinstance(item, CustomCharge):
        return BillableItemType.CUSTOM_CHARGE
    elif isinstance(item, TrainingSession):
        return BillableItemType.TRAINING
    elif isinstance(item, ConsumableWithdraw):
        return BillableItemType.CONSUMABLE


# We are rounding to the next penny
def round_decimal_amount(value: Union[decimal.Decimal, int, float]):
    if isinstance(value, decimal.Decimal):
        decimal_value = value
    else:
        decimal_value = decimal.Decimal(str(value))
    return decimal_value.quantize(decimal.Decimal("0.01"), rounding=decimal.ROUND_UP)


# This will round up to the next second, but then keep as much precision as possible for calculations
# Remove when changed in NEMO
def get_minutes_between_dates(start, end) -> decimal.Decimal:
    diff: datetime.timedelta = end - start
    return decimal.Decimal(math.ceil(diff.total_seconds())) / decimal.Decimal(60)
