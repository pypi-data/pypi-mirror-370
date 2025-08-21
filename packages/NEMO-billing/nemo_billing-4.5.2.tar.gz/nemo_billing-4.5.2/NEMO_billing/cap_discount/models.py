from __future__ import annotations

from datetime import MAXYEAR, MINYEAR, date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from NEMO.constants import CHAR_FIELD_SMALL_LENGTH
from NEMO.models import Account, BaseModel, User
from NEMO.typing import QuerySetType
from NEMO.utilities import RecurrenceFrequency, format_datetime, get_recurring_rule
from dateutil.rrule import rrule
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, validate_comma_separated_integer_list
from django.db import IntegrityError, models, transaction
from django.db.models import Q, UniqueConstraint
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from NEMO_billing.invoices.models import BillableItemType
from NEMO_billing.models import CoreFacility
from NEMO_billing.rates.models import RateCategory
from NEMO_billing.utilities import Months


class CAPDiscountConfiguration(BaseModel):
    rate_category = models.ForeignKey(
        RateCategory, help_text="The rate category this CAP applies to", on_delete=models.CASCADE
    )
    core_facilities = models.ManyToManyField(
        CoreFacility,
        blank=True,
        help_text="The core facility(ies) this CAP applies to. If multiple are selected, the CAP is shared between facilities",
    )
    charge_types = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=CHAR_FIELD_SMALL_LENGTH,
        help_text="List of charge type this CAP applies to",
    )
    start_on_first_charge = models.BooleanField(
        default=True, help_text="Automatically set CAP start date to the month of the first eligible charge"
    )
    split_by_user = models.BooleanField(
        default=True,
        help_text="Check this box to have a separate CAP amount per each user/account. If unchecked, the CAP will be per account only (all user charges count towards the same CAP)",
    )
    # Recurring schedule
    start_month = models.PositiveIntegerField(
        null=True, blank=True, choices=Months.choices, help_text="Start month of the CAP discount"
    )
    start_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Start year of the CAP discount",
        validators=[MinValueValidator(1900), MaxValueValidator(MAXYEAR)],
    )
    reset_interval = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Recurring interval, i.e. every 5 days.",
    )
    reset_frequency = models.PositiveIntegerField(
        choices=[
            (RecurrenceFrequency.MONTHLY.index, RecurrenceFrequency.MONTHLY.display_value),
            (RecurrenceFrequency.YEARLY.index, RecurrenceFrequency.YEARLY.display_value),
        ],
        help_text="The CAP reset frequency.",
    )

    @property
    def start(self) -> date:
        if self.start_year and self.start_month:
            return date(self.start_year, self.start_month, 1)

    @start.setter
    def start(self, value: date):
        if value:
            self.start_month, self.start_year = value.month, value.year
        else:
            self.start_month, self.start_year = None, None

    @property
    def billable_charge_types(self) -> List[BillableItemType]:
        return [BillableItemType(int(value)) for value in self.charge_types.split(",") if value]

    @property
    def core_facility_names(self) -> Tuple[str]:
        return tuple(cf.name for cf in self.core_facilities.all())

    @property
    def get_reset_frequency_enum(self):
        return RecurrenceFrequency(self.reset_frequency)

    def clean(self):
        errors = {}
        # We need to check ids otherwise it will throw a RelatedObjectDoesNotExist if they are not set even if required
        if self.start_month and not self.start_year or self.start_year and not self.start_month:
            errors["start_year"] = "Both year/month are required together"
            errors["start_month"] = "Both year/month are required together"
        if not self.start and not self.start_on_first_charge:
            errors["start_year"] = "Year is required when `Start on first charge` is unchecked."
            errors["start_month"] = "Month is required when `Start on first charge` is unchecked."
        if self.start and self.start_on_first_charge:
            errors["start_on_first_charge"] = "You entered a start date, remove it or unchecked this box."
        if errors:
            raise ValidationError(errors)

    def get_recurrence_interval_display(self) -> str:
        if not self.reset_frequency:
            return ""
        interval = f"{self.reset_interval} " if self.reset_interval != 1 else ""
        f_enum = self.get_reset_frequency_enum
        frequency = f"{f_enum.display_text}s" if self.reset_interval != 1 else f_enum.display_text
        return f"Every {interval}{frequency}"

    @transaction.atomic
    def get_or_create_cap_discount(self, account: Account, username: Optional[str], start: date):
        try:
            # Cap discount exists, return it
            return CAPDiscount.objects.get(configuration=self, account=account, user__username=username)
        except CAPDiscount.DoesNotExist:
            # Cap discount doesn't exist, create it
            user = User.objects.get(username=username) if username else None
            new_cap_discount = CAPDiscount(configuration=self, account=account, user=user)
            cap_discount_tiers = self.initialize_cap_discount_and_get_tiers(new_cap_discount)
            if self.start_on_first_charge:
                assert start is not None
                new_cap_discount.start = start
            new_cap_discount.save()
            # Now that we saved our new cap discount, save related tiers and initialize amounts
            new_cap_discount.save_related_cap_tiers(cap_discount_tiers)
            assert new_cap_discount.start is not None
            CAPDiscountAmount.objects.create(
                cap_discount=new_cap_discount, year=start.year, month=start.month, start=0, end=0
            )
            # Also create first amount
            return new_cap_discount

    def initialize_cap_discount_and_get_tiers(self, cap_discount: CAPDiscount) -> List[CAPDiscountTier]:
        # Initialize cap discount and return cap discount tiers to be saved later
        if self.start and not self.start_on_first_charge:
            cap_discount.start = self.start
        cap_discount.reset_interval = self.reset_interval
        cap_discount.reset_frequency = self.reset_frequency
        cap_discount.charge_types = self.charge_types
        return self.copy_cap_discount_tiers(cap_discount)

    def copy_cap_discount_tiers(self, cap_discount: CAPDiscount) -> List[CAPDiscountTier]:
        # Copy the discount tiers by creating new ones for the cap discount
        tiers = []
        for cap_discount_tier in self.capdiscounttier_set.all():
            tiers.append(
                CAPDiscountTier(
                    cap_discount=cap_discount, amount=cap_discount_tier.amount, discount=cap_discount_tier.discount
                )
            )
        return tiers

    def __str__(self):
        facilities = f"{','.join(self.core_facility_names)}/" if self.core_facilities.exists() else ""
        return f"CAP Discount for {facilities}{self.rate_category.name}"


# We have no choice but to check for uniqueness here, since many to many fields cannot be used
# in validate_unique or in clean methods
@receiver(m2m_changed, sender=CAPDiscountConfiguration.core_facilities.through)
def validate_unique_cap_config(sender, instance: CAPDiscountConfiguration, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        matching_config: QuerySetType[CAPDiscountConfiguration] = CAPDiscountConfiguration.objects.filter(
            rate_category=instance.rate_category
        ).exclude(pk=instance.pk)
        match: Optional[CAPDiscountConfiguration] = None
        if not instance.core_facilities.exists():
            match = matching_config.filter(core_facilities__isnull=True).first()
        else:
            for cap_config in matching_config:
                cap_config_facilities = set(cap_config.core_facilities.all())
                intersection = cap_config_facilities.intersection(instance.core_facilities.all())
                if intersection:
                    match = cap_config
                    break
        if match:
            raise IntegrityError(
                f"There is already a CAP Configuration for {instance.rate_category} and the selected core facility(ies): {match}"
            )


class CAPDiscount(BaseModel):
    configuration = models.ForeignKey(
        CAPDiscountConfiguration, help_text="The configuration for this CAP", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, blank=True, null=True, help_text="The user this CAP applies to", on_delete=models.CASCADE
    )
    account = models.ForeignKey(Account, help_text="The account this CAP applies to", on_delete=models.CASCADE)
    charge_types = models.CharField(
        validators=[validate_comma_separated_integer_list],
        max_length=CHAR_FIELD_SMALL_LENGTH,
        help_text="List of charge type this CAP applies to",
    )
    # Recurring schedule
    start_month = models.PositiveIntegerField(
        null=True, blank=True, choices=Months.choices, help_text="Start month of the CAP discount"
    )
    start_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Start year of the CAP discount",
        validators=[MinValueValidator(1900), MaxValueValidator(MAXYEAR)],
    )
    next_reset_override_month = models.PositiveIntegerField(
        null=True, blank=True, choices=Months.choices, help_text="Temporary one-time reset override month"
    )
    next_reset_override_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Temporary one-time reset override year",
        validators=[MinValueValidator(1900), MaxValueValidator(MAXYEAR)],
    )
    reset_interval = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Recurring interval, i.e. every 5 days.",
    )
    reset_frequency = models.PositiveIntegerField(
        choices=[
            (RecurrenceFrequency.MONTHLY.index, RecurrenceFrequency.MONTHLY.display_value),
            (RecurrenceFrequency.YEARLY.index, RecurrenceFrequency.YEARLY.display_value),
        ],
        help_text="The CAP reset frequency.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Temporary variables used for discount calculations
        self.tmp_current_amount: Optional[Decimal] = None
        # Dict of project_id -> core facility -> Decimal
        self.tmp_project_discounts: Dict[int, Dict[str, Decimal]] = {}

    @property
    def start(self) -> date:
        if self.start_year and self.start_month:
            return date(self.start_year, self.start_month, 1)

    @start.setter
    def start(self, value: date):
        if value:
            self.start_month, self.start_year = value.month, value.year
        else:
            self.start_month, self.start_year = None, None

    @property
    def next_reset_override(self) -> date:
        if self.next_reset_override_year and self.next_reset_override_month:
            return date(self.next_reset_override_year, self.next_reset_override_month, 1)

    @next_reset_override.setter
    def next_reset_override(self, value: date):
        if value:
            self.next_reset_override_month, self.next_reset_override_year = value.month, value.year
        else:
            self.next_reset_override_month, self.next_reset_override_year = None, None

    @property
    def billable_charge_types(self) -> List[BillableItemType]:
        return [BillableItemType(int(value)) for value in self.charge_types.split(",") if value]

    @property
    def get_reset_frequency_enum(self):
        return RecurrenceFrequency(self.reset_frequency)

    def get_recurrence(self) -> rrule:
        if self.start and self.reset_frequency:
            return get_recurring_rule(self.start, self.get_reset_frequency_enum, interval=self.reset_interval)

    def get_recurrence_interval_display(self) -> str:
        if not self.start or not self.reset_frequency:
            return ""
        interval = f"{self.reset_interval} " if self.reset_interval != 1 else ""
        f_enum = self.get_reset_frequency_enum
        frequency = f"{f_enum.display_text}s" if self.reset_interval != 1 else f_enum.display_text
        return f"Every {interval}{frequency}"

    def get_recurrence_display(self) -> str:
        display = ""
        if self.start and self.reset_frequency:
            return f"{self.get_recurrence_interval_display()}, starting {format_datetime(self.start, 'F Y')}"
        return display

    def next_reset_date_after(self, dt: date, inc=False) -> datetime:
        if self.next_reset_override:
            return datetime(self.next_reset_override.year, self.next_reset_override.month, self.next_reset_override.day)
        dt_datetime = datetime(dt.year, dt.month, dt.day)
        recurrence = self.get_recurrence()
        return recurrence.after(dt_datetime, inc=inc) if recurrence else None

    def next_reset(self, inc=False) -> datetime:
        return self.next_reset_date_after(date.today(), inc=inc)

    def last_reset(self) -> datetime:
        recurrence = self.get_recurrence()
        return recurrence.before(datetime.now(), inc=False) if recurrence else None

    @transaction.atomic
    def reset(self):
        # Reinitialize based on the linked configuration, and blank out reset override
        cap_discount_tiers = self.configuration.initialize_cap_discount_and_get_tiers(self)
        # Save the new tiers
        self.save_related_cap_tiers(cap_discount_tiers)
        if self.next_reset_override and self.configuration.start_on_first_charge:
            # We are resetting the start date/month to the override to keep the recurrence correct
            self.start = self.next_reset_override
        self.next_reset_override = None
        self.save()

    def latest_amount(self) -> CAPDiscountAmount:
        return self.capdiscountamount_set.latest("year", "month")

    def earliest_amount(self) -> CAPDiscountAmount:
        return self.capdiscountamount_set.earliest("year", "month")

    def save_related_cap_tiers(self, cap_discount_tiers):
        for cap_discount_tier in cap_discount_tiers:
            cap_discount_tier.save()
        self.capdiscounttier_set.set(cap_discount_tiers)

    def clean(self):
        errors = {}
        # We need to check ids otherwise it will throw a RelatedObjectDoesNotExist if they are not set even if required
        if self.account_id and self.user_id and not self.user.projects.filter(account=self.account).exists():
            errors["account"] = "This user doesn't belong to this account"
        if self.start_month and not self.start_year or self.start_year and not self.start_month:
            errors["start_year"] = "Both year/month are required together"
            errors["start_month"] = "Both year/month are required together"
        if (
            self.next_reset_override_month
            and not self.next_reset_override_year
            or self.next_reset_override_year
            and not self.next_reset_override_month
        ):
            errors["next_reset_override_year"] = "Both year/month are required together"
            errors["next_reset_override_month"] = "Both year/month are required together"
        this_month = date(date.today().year, date.today().month, 1)
        if self.next_reset_override is not None and self.next_reset_override < this_month:
            errors["next_reset_override_year"] = "The override date cannot be in the past."
            errors["next_reset_override_month"] = "The override date cannot be in the past."
        if errors:
            raise ValidationError(errors)

    def estimated_charges_since_last_update(self) -> Decimal:
        from NEMO_billing.cap_discount.processors import CAPDiscountInvoiceDataProcessor

        return CAPDiscountInvoiceDataProcessor().estimated_charges_since_last_update(self)

    def current_level_reached(self) -> CAPDiscountTier:
        total_current_charges = self.latest_amount().end + self.estimated_charges_since_last_update()
        for tier in self.capdiscounttier_set.all().reverse():
            if total_current_charges > tier.amount:
                return tier

    def __str__(self):
        username = f"/{self.user.username}" if self.user else ""
        facilities = (
            f"{','.join(self.configuration.core_facility_names)}/"
            if self.configuration.core_facilities.exists()
            else ""
        )
        return f"CAP Discount for {facilities}{self.account}/{self.configuration.rate_category.name}{username}"

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["configuration", "account", "user"],
                name="%(app_label)s_%(class)s_unique_config_account_user",
            ),
            UniqueConstraint(
                fields=["configuration", "account"],
                condition=Q(user=None),
                name="%(app_label)s_%(class)s_unique_config_account_null_user",
            ),
        ]


class CAPDiscountTier(BaseModel):
    cap_discount_configuration = models.ForeignKey(
        CAPDiscountConfiguration, null=True, blank=True, on_delete=models.CASCADE
    )
    cap_discount = models.ForeignKey(CAPDiscount, null=True, blank=True, on_delete=models.CASCADE)
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=14,
        help_text="Amount after which the discount will be applied",
        validators=[MinValueValidator(1)],
    )
    discount = models.DecimalField(
        decimal_places=3,
        max_digits=6,
        help_text="Discount in percent. Ex 20.5%",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    def discount_amount(self) -> Decimal:
        return -self.discount / Decimal(100)

    def clean(self):
        if not self.cap_discount and not self.cap_discount_configuration:
            raise ValidationError("One of cap discount or cap discount configuration needs to be set")
        if self.cap_discount and self.cap_discount_configuration:
            raise ValidationError("Discount tiers cannot be linked to both cap discount and cap discount configuration")

    class Meta:
        ordering = ["amount"]

    def __str__(self):
        return f"> {str(self.amount).rstrip('0').rstrip('.')} -> {str(self.discount).rstrip('0').rstrip('.')} %"


class CAPDiscountAmount(BaseModel):
    cap_discount = models.ForeignKey(CAPDiscount, on_delete=models.CASCADE)
    month = models.PositiveIntegerField(choices=Months.choices)
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(MINYEAR), MaxValueValidator(MAXYEAR)],
    )
    start = models.DecimalField(decimal_places=2, max_digits=14)
    end = models.DecimalField(decimal_places=2, max_digits=14)

    def new_charges(self):
        return (self.end or 0) - (self.start or 0)

    @property
    def amount_date(self) -> date:
        if self.year and self.month:
            return date(self.year, self.month, 1)

    @amount_date.setter
    def amount_date(self, value: date):
        if value:
            self.month, self.year = value.month, value.year
        else:
            self.month, self.year = None, None

    def __str__(self):
        return f"CAP #{self.cap_discount.id}, {self.get_month_display()} {self.year}, {self.start} -> {self.end}"

    class Meta:
        ordering = ["-year", "-month"]
        unique_together = ["cap_discount", "month", "year"]
