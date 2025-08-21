from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from logging import getLogger
from typing import Any, List, Optional, Tuple

from NEMO.constants import CHAR_FIELD_MEDIUM_LENGTH, CHAR_FIELD_SMALL_LENGTH
from NEMO.models import Area, BaseModel, Consumable, Tool, User
from NEMO.utilities import format_datetime, slugify_underscore
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.db.models import Model, QuerySet
from django.urls import reverse
from django.utils.safestring import mark_safe
from mptt.fields import TreeForeignKey

from NEMO_billing.rates.model_diff import ModelDiff
from NEMO_billing.utilities import round_decimal_amount

model_logger = getLogger(__name__)


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MIDNIGHT = time(0, 0, 0, 0)


class ActionLog(object):
    ADD = 0
    DELETE = 1
    UPDATE = 2
    Choices = ((ADD, "Add"), (DELETE, "Delete"), (UPDATE, "Update"))


class RateCategory(BaseModel):
    name = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH, help_text="The name of this rate category", unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Rate category"
        verbose_name_plural = "Rate categories"
        ordering = ["name"]


class RateType(BaseModel):
    class Type(object):
        TOOL = "Tool"
        TOOL_USAGE = "TOOL_USAGE"
        TOOL_TRAINING_INDIVIDUAL = "TOOL_TRAINING_INDIVIDUAL"
        TOOL_TRAINING_GROUP = "TOOL_TRAINING_GROUP"
        TOOL_MISSED_RESERVATION = "TOOL_MISSED_RESERVATION"
        AREA = "Area"
        AREA_USAGE = "AREA_USAGE"
        AREA_MISSED_RESERVATION = "AREA_MISSED_RESERVATION"
        CONSUMABLE = "CONSUMABLE"
        STAFF_CHARGE = "STAFF_CHARGE"
        choices = [
            (
                TOOL,
                (
                    (TOOL_USAGE, "Tool usage"),
                    (TOOL_TRAINING_INDIVIDUAL, "Tool individual training"),
                    (TOOL_TRAINING_GROUP, "Tool group training"),
                    (TOOL_MISSED_RESERVATION, "Tool missed reservation"),
                ),
            ),
            (AREA, ((AREA_USAGE, "Area usage"), (AREA_MISSED_RESERVATION, "Area missed reservation"))),
            (CONSUMABLE, "Consumable/Supply"),
            (STAFF_CHARGE, "Staff charge"),
        ]

    type = models.CharField(max_length=CHAR_FIELD_SMALL_LENGTH, choices=Type.choices)
    category_specific = models.BooleanField(
        default=False,
        help_text="Check this box to make this rate type category specific (i.e. you will need to enter a rate for each category)",
    )
    item_specific = models.BooleanField(
        default=False,
        help_text="Check this box to make this rate type item specific (i.e. you will need to enter a rate for each item)",
    )

    def is_tool_rate(self):
        return self.type in [
            self.Type.TOOL_MISSED_RESERVATION,
            self.Type.TOOL_USAGE,
            self.Type.TOOL_TRAINING_INDIVIDUAL,
            self.Type.TOOL_TRAINING_GROUP,
        ]

    def is_area_rate(self):
        return self.type in [self.Type.AREA_USAGE, self.Type.AREA_MISSED_RESERVATION]

    def is_consumable_rate(self):
        return self.type == self.Type.CONSUMABLE

    def is_staff_charge_rate(self):
        return self.type == self.Type.STAFF_CHARGE

    def get_rate_group_type(self) -> str:
        if self.is_tool_rate() and self.item_specific:
            return RateType.Type.TOOL
        elif self.is_area_rate() and self.item_specific:
            return RateType.Type.AREA
        else:
            return self.type

    def can_have_rate_time(self):
        return self.type not in [
            RateType.Type.CONSUMABLE,
            RateType.Type.TOOL_TRAINING_GROUP,
            RateType.Type.TOOL_TRAINING_INDIVIDUAL,
        ]

    def clean(self):
        if (
            self.type
            and not self.item_specific
            and self.type in [self.Type.TOOL_USAGE, self.Type.AREA_USAGE, self.Type.CONSUMABLE]
        ):
            raise ValidationError({"item_specific": "This rate has to be item specific"})

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)
        if not exclude or exclude and "type" not in exclude and self.type:
            if RateType.objects.filter(type=self.type).exclude(id=self.pk).exists():
                raise ValidationError({"type": f"There is already a {self.get_type_display()} rate type"})

    def __str__(self):
        return self.get_type_display()


class RateTime(BaseModel):
    name = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH, unique=True)

    def earliest_match(self, start_time: datetime, end_time: datetime) -> Optional[Tuple[datetime, datetime]]:
        # This function returns the earliest start (and end time) this time applies to in the daterange if any.
        # For example if this RateTime is MON-FRI 4-5PM, given a start (MON 3PM) and end (MON 8PM),
        # It will send back the earliest start & end date times (MON 4PM to MON 5PM) when this applies
        start_time_utc = start_time.astimezone(timezone.utc)
        end_time_utc = end_time.astimezone(timezone.utc)
        possible_dates: List[Tuple[datetime, datetime]] = []
        # Loop over 2 weeks, to make sure we go over all days
        for i in [0, 1]:
            datetime_control = start_time_utc + timedelta(weeks=i)
            for time_and_day in self.dailyschedule_set.all():
                start_datetime, end_datetime = time_and_day.datetime_range(datetime_control)
                # If there is overlap, add start to list
                if (start_time_utc < end_datetime) and (end_time_utc > start_datetime):
                    possible_dates.append((max(start_time_utc, start_datetime), min(end_time_utc, end_datetime)))
        return min(possible_dates) if possible_dates else (None, None)

    def overlaps(self, rate_time) -> bool:
        # Function returning whether this rate time overlaps with another
        # They overlap if any of their schedules overlap
        control_datetime = datetime.today()
        for daily_schedule in self.dailyschedule_set.all():
            for other_daily_schedule in rate_time.dailyschedule_set.all():
                if daily_schedule.overlaps(control_datetime, other_daily_schedule):
                    return True
        return False

    def __str__(self):
        return self.name


class DailySchedule(BaseModel):
    rate_time = models.ForeignKey(RateTime, on_delete=models.CASCADE)
    weekday = models.IntegerField(
        verbose_name="start day", choices=[(DAYS.index(day_name), day_name) for day_name in DAYS]
    )
    start_time = models.TimeField(blank=True, null=True, help_text="The start time")
    end_time = models.TimeField(blank=True, null=True, help_text="The end time")

    def datetime_range(self, control_datetime) -> (datetime, datetime):
        # Given a control datetime, a weekday, start and end time, returns a full datetime range
        beginning_of_the_week = control_datetime - timedelta(days=control_datetime.weekday())
        start_day = beginning_of_the_week + timedelta(days=self.weekday)
        start_datetime = datetime.combine(start_day, self.start_time or MIDNIGHT).astimezone(control_datetime.tzinfo)
        end_datetime = start_datetime + timedelta(seconds=self.duration().total_seconds())
        return start_datetime, end_datetime

    def overlaps(self, control_datetime: datetime, daily_schedule) -> bool:
        first_start, first_end = self.datetime_range(control_datetime)
        second_start, second_end = daily_schedule.datetime_range(control_datetime)
        return first_start < second_end and first_end > second_start

    def is_time_range_split(self):
        # Returns whether the time range is across 2 days, like 6pm - 6am
        # We have to treat midnight separately since 6pm - 12am is not split even though 6pm is technically after 12am
        return self.start_time and self.end_time and self.start_time >= self.end_time != MIDNIGHT

    def duration(self) -> timedelta:
        today = datetime.today()
        start_datetime = datetime.combine(today, self.start_time or MIDNIGHT)
        end_datetime = datetime.combine(today, self.end_time or MIDNIGHT)
        end_edge_cases = not self.end_time or self.end_time == MIDNIGHT or self.end_time == self.start_time
        if self.is_time_range_split() or end_edge_cases:
            end_datetime = end_datetime + timedelta(days=1)
        return end_datetime - start_datetime

    def clean(self):
        errors = {}
        if self.weekday == 6 and self.is_time_range_split():
            errors["end_time"] = ValidationError(
                "Sunday schedule has to end at Midnight at the latest (add a Monday schedule if needed)"
            )
        # Check for rates already using this time
        if self.rate_time and self.rate_time.pk:
            control_datetime = datetime.today()
            for rate in self.rate_time.rate_set.all():
                rate_filter = rate.rate_queryset_uniqueness()
                if rate_filter.exists():
                    # Check for overlapping times on previous rates
                    for other_rate_with_time in rate_filter:
                        for other_daily_schedule in other_rate_with_time.time.dailyschedule_set.all():
                            if self.overlaps(control_datetime, other_daily_schedule):
                                link = reverse("admin:rates_ratetime_change", args=[other_rate_with_time.time.id])
                                errors[NON_FIELD_ERRORS] = ValidationError(
                                    mark_safe(
                                        f'This time would now overlap with {other_rate_with_time}<br>Click <a href="{link}">here</a> to change the other rate time'
                                    )
                                )
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        end_time = (
            format_datetime(self.end_time)
            if self.end_time and not self.end_time == MIDNIGHT and not self.is_time_range_split()
            else f"{next_as_loop(DAYS, self.get_weekday_display())}, {format_datetime(self.end_time or MIDNIGHT)}"
        )
        return f"{self.get_weekday_display()}, {format_datetime(self.start_time or MIDNIGHT)} to {end_time}"

    class Meta:
        ordering = ("weekday", "start_time")


class Rate(BaseModel):
    type = models.ForeignKey(RateType, on_delete=models.CASCADE)
    time = models.ForeignKey(RateTime, null=True, blank=True, on_delete=models.CASCADE)
    category = models.ForeignKey(RateCategory, null=True, blank=True, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, null=True, blank=True, on_delete=models.CASCADE)
    area = TreeForeignKey(Area, null=True, blank=True, on_delete=models.CASCADE)
    consumable = models.ForeignKey(Consumable, null=True, blank=True, on_delete=models.CASCADE)
    amount = models.DecimalField(
        decimal_places=2, max_digits=8, help_text="The rate per hour if this isn't a flat rate"
    )
    effective_date = models.DateField(blank=True, null=True, help_text="The date when this rate becomes effective.")
    flat = models.BooleanField(default=False, help_text="Check this box to make this a flat rate (independent of time)")
    daily = models.BooleanField(default=False, help_text="Check this box to only charge once per day for this item")
    daily_split_multi_day_charges = models.BooleanField(
        default=True,
        help_text="Check this box to split charges spanning multiple days, leave unchecked to keep one long charge",
    )
    minimum_charge = models.DecimalField(
        decimal_places=2, max_digits=8, null=True, blank=True, help_text="The minimum charge for this rate"
    )
    deleted = models.BooleanField(default=False, help_text="Indicates that this rate was deleted")

    @classmethod
    def non_deleted(cls):
        return cls.objects.filter(deleted=False)

    def natural_identifier(self):
        """
        Generates a natural identifier (from type, category and item) that represents the rate (not the instance).
        Times, effective dates and attributes like flat or minimum amount are not part of the identifier.
        """
        item = self.get_item()
        if isinstance(item, Model):
            item_content_type_id = ContentType.objects.get_for_model(item).id
            item_id = item.id
        else:
            item_content_type_id = "none"
            item_id = slugify_underscore(item).lower() if item else "none"
        components = [
            f"type:{self.type_id}",  # Rate type ID
            f"category:{self.category_id or 'none'}",  # Category ID, use 'none' if not applicable
            f"item_content_type:{item_content_type_id or 'none'}",
            f"item:{item_id or 'none'}",  # Tool/Area/Consumable ID or 'staff_charge' or 'none'
        ]
        return "|".join(components)

    def get_item(self):
        if self.type.is_tool_rate():
            return self.tool
        elif self.type.is_area_rate():
            return self.area
        elif self.type.is_consumable_rate():
            return self.consumable
        elif self.type.is_staff_charge_rate():
            return "Staff charge"
        return None

    get_item.short_description = "Item"

    def clean(self):
        errors = {}
        if self.type_id:
            if self.type.is_tool_rate():
                if self.area or self.consumable:
                    errors[NON_FIELD_ERRORS] = ValidationError(
                        "You cannot select an area or a consumable for a tool rate"
                    )
                if self.type.item_specific and not self.tool:
                    errors["tool"] = ValidationError("You need to select a tool for this rate type")
            elif self.type.is_area_rate():
                if self.tool or self.consumable:
                    errors[NON_FIELD_ERRORS] = ValidationError(
                        "You cannot select a tool or a consumable for a area rate"
                    )
                if self.type.item_specific and not self.area:
                    errors["area"] = ValidationError("You need to select an area for this rate type")
            elif self.type.is_consumable_rate():
                if self.tool or self.area:
                    errors[NON_FIELD_ERRORS] = ValidationError(
                        "You cannot select a tool or an area for a consumable rate"
                    )
                if self.type.item_specific and not self.consumable:
                    errors["consumable"] = ValidationError("You need to select a consumable for this rate type")
                if not self.flat:
                    errors["flat"] = ValidationError("Consumable rates are flat rates")
            elif self.type.is_staff_charge_rate():
                if self.tool or self.consumable or self.area:
                    errors[NON_FIELD_ERRORS] = ValidationError(
                        "You cannot select a tool, area or consumable for a staff charge rate"
                    )
            if not self.type.item_specific and (self.tool or self.consumable or self.area):
                errors[NON_FIELD_ERRORS] = ValidationError(
                    "You cannot select a tool, area or consumable for a non item specific rate type"
                )
            if RateCategory.objects.exists() and self.type.category_specific and not self.category:
                errors["category"] = ValidationError("This rate type is category specific. Please select a category")
            if not self.type.category_specific and self.category:
                errors["category"] = ValidationError("The rate type you selected is not category specific")
            if self.daily:
                if self.type.type not in [RateType.Type.TOOL_USAGE, RateType.Type.AREA_USAGE]:
                    errors["daily"] = ValidationError("Only tool and area usage can be set to daily charge")
                if not self.flat:
                    errors["flat"] = ValidationError("Daily charges should be flat")
            # We cannot have different rate times for Consumable or Training rates
            if self.time:
                if not self.type.can_have_rate_time():
                    errors["time"] = ValidationError("This rate type doesn't allow different rate times")
                elif self.flat:
                    errors["time"] = ValidationError("A flat rate cannot have different schedule/times")
        if errors:
            raise ValidationError(errors)

    def rate_queryset_uniqueness(self) -> QuerySet:
        # This function returns a queryset used to check for other rates of the same type and category/item if applicable
        # Essentially a type that is category_specific but no categories exist is the same as non category specific
        category_specific = self.type.category_specific and RateCategory.objects.exists()
        rate_filter = Rate.non_deleted().filter(time__isnull=not self.time).exclude(pk=self.pk)
        if self.effective_date:
            rate_filter = rate_filter.filter(effective_date=self.effective_date)
        else:
            rate_filter = rate_filter.filter(effective_date__isnull=True)
        if not category_specific and not self.type.item_specific:
            rate_filter = rate_filter.filter(type=self.type)
        elif not category_specific and self.type.item_specific:
            rate_filter = self.rate_item_filter(rate_filter.filter(type=self.type))
        elif category_specific and self.type.item_specific:
            rate_filter = self.rate_item_filter(rate_filter.filter(type=self.type, category=self.category))
        elif category_specific and not self.type.item_specific:
            rate_filter = rate_filter.filter(type=self.type, category=self.category)
        return rate_filter

    def rate_item_filter(self, queryset: QuerySet) -> QuerySet:
        if self.type:
            if self.type.is_tool_rate():
                return queryset.filter(tool=self.tool)
            elif self.type.is_area_rate():
                return queryset.filter(area=self.area)
            elif self.type.is_consumable_rate():
                return queryset.filter(consumable=self.consumable)
        return queryset

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)
        if not exclude or exclude and "type" not in exclude and self.type:
            error_message = f"A rate of this type already exists or overlaps this one"
            rate_filter = self.rate_queryset_uniqueness()
            if rate_filter.exists():
                # If we have a time, check for overlapping times on previous rates
                if self.time:
                    for other_rate_with_time in rate_filter:
                        if self.time.overlaps(other_rate_with_time.time):
                            raise ValidationError(mark_safe(f"{error_message}: {str(other_rate_with_time)}"))
                else:
                    already_existing_rate = rate_filter.first()
                    raise ValidationError(mark_safe(f"{error_message}: {str(already_existing_rate)}"))

    # Use this method instead of regular save to allow rates audit log
    def save_with_user(self, user: User, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            rate_pre_save_log(self, user)
        except Exception as e:
            model_logger.exception(e)
        super().save(force_insert, force_update, using, update_fields)

    def delete_with_user(self, user: User):
        try:
            rate_pre_delete_log(self, user)
        except Exception as e:
            model_logger.exception(e)
        self.deleted = True
        self.save(update_fields=["deleted"])

    def is_hourly_rate(self):
        return self.type.type in [
            RateType.Type.TOOL_USAGE,
            RateType.Type.AREA_USAGE,
            RateType.Type.STAFF_CHARGE,
            RateType.Type.TOOL_TRAINING_GROUP,
            RateType.Type.TOOL_TRAINING_INDIVIDUAL,
            RateType.Type.AREA_MISSED_RESERVATION,
            RateType.Type.TOOL_MISSED_RESERVATION,
        ]

    def display_rate(self) -> str:
        return self.display_rate_value(self.amount, self.minimum_charge)

    def display_rate_value(self, amount_value, minimum_charge):
        amount = f"{amount_value:.2f}"
        if self.is_hourly_rate():
            if self.daily:
                # Display daily explicitly when we have an hourly rate set as daily
                amount = f"daily {amount}"
            elif self.flat:
                # Display flat explicitly when we have an hourly rate set as flat
                amount = f"flat {amount}"
            else:
                # Display hourly when we have an hourly rate not set as flat
                amount = f"{amount}/hr"
        minimum = f" ({minimum_charge:.2f} minimum)" if minimum_charge else ""
        return f"{amount}{minimum}"

    def calculate_amount(self, quantity: Decimal) -> Decimal:
        effective_quantity = quantity
        if self.is_hourly_rate():
            if self.flat:
                # If hourly rate is set as flat, disregard quantity
                effective_quantity = 1
            else:
                # Otherwise, divide by 60 since quantity is in minutes
                effective_quantity = quantity / Decimal(60)
        amount = effective_quantity * self.amount
        if self.minimum_charge:
            amount = max(amount, self.minimum_charge)
        return round_decimal_amount(amount)

    def display_category_time(self):
        category = self.category.name if self.category else None
        rate_time = self.time.name if self.time else None
        cat_time = (
            [category, rate_time]
            if category and rate_time
            else [category] if category else [rate_time] if rate_time else []
        )
        return f" ({'/'.join(cat_time)})" if cat_time else ""

    def quote_display(self):
        item_name = f"{self.get_item()} " if self.get_item() else ""
        category = f" ({self.category})" if self.category else ""
        rate_time = f", {self.time}" if self.time else ""
        return f"[{self.type}] {item_name}{category}{rate_time}"

    def __str__(self):
        item_name = f"{self.get_item()} " if self.get_item() else ""
        category = f" ({self.category})" if self.category else ""
        rate_time = f", {self.time}" if self.time else ""
        effective_date = f", effective {format_datetime(self.effective_date)}" if self.effective_date else ""
        return f"{item_name}{self.type}{category}{rate_time}{effective_date}"


class AreaHighestDailyRateGroup(BaseModel):
    areas = models.ManyToManyField(
        Area,
        help_text="Select all areas that require grouping daily, and for which only the most expensive one will be charged.",
    )


class RateLog(BaseModel):
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    action = models.IntegerField(choices=ActionLog.Choices)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    details = models.TextField(null=True, blank=True)


def get_rate_content_object(rate: Rate):
    item = rate.get_item()
    return item if isinstance(item, models.Model) else None


def rate_pre_save_log(rate: Rate, user: User):
    try:
        original: Rate = Rate.objects.get(pk=rate.pk)
    except Rate.DoesNotExist:
        RateLog.objects.create(
            action=ActionLog.ADD,
            user=user,
            content_object=get_rate_content_object(rate),
            details=ModelDiff(rate).model_diff_display,
        )
    else:
        model_diff = ModelDiff(original, rate)
        if model_diff.has_changed():
            RateLog.objects.create(
                action=ActionLog.UPDATE,
                user=user,
                content_object=get_rate_content_object(original),
                details=model_diff.model_diff_display,
            )


def rate_pre_delete_log(rate: Rate, user: User):
    RateLog.objects.create(
        action=ActionLog.DELETE,
        user=user,
        content_object=get_rate_content_object(rate),
        details=ModelDiff(rate).model_diff_display,
    )


def next_as_loop(elements: List, match: Any, backwards=False) -> Any:
    # this function returns the next element after the match, looping back to the beginning if the match is the last one
    # or if reverse is True, the previous element before the match, looping back to the end if match is first element
    # For example, next_as_loop([1,2,3,4,5], 5) will return 1 and next_as_loop([1,2,3,4,5], 1, backwards) will return 5
    index_match = elements.index(match)
    if not backwards:
        return elements[0] if index_match == len(elements) - 1 else elements[index_match + 1]
    else:
        return elements[len(elements) - 1] if index_match == 0 else elements[index_match - 1]
