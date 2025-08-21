from __future__ import annotations

import os
from datetime import timedelta
from decimal import Decimal
from enum import Enum, unique
from logging import getLogger
from typing import Dict, List

from NEMO import fields
from NEMO.constants import CHAR_FIELD_LARGE_LENGTH, CHAR_FIELD_MEDIUM_LENGTH, CHAR_FIELD_SMALL_LENGTH
from NEMO.models import BaseCategory, BaseModel, Customization, Project, SerializationByNameModel, User
from NEMO.utilities import create_email_attachment
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Case, Q, Sum, When
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from NEMO_billing.invoices.utilities import (
    category_name_for_item_type,
    display_amount,
    export_invoice_filename,
    get_invoice_document_filename,
    get_merchant_logo_filename,
    render_and_send_email,
)
from NEMO_billing.rates.models import Rate, RateCategory, RateType


@unique
class BillableItemType(Enum):
    TOOL_USAGE = 1
    AREA_ACCESS = 2
    CONSUMABLE = 3
    MISSED_RESERVATION = 4
    STAFF_CHARGE = 5
    TRAINING = 6
    CUSTOM_CHARGE = 7

    @classmethod
    def choices(cls):
        return (
            (cls.TOOL_USAGE.value, "tool_usage"),
            (cls.AREA_ACCESS.value, "area_access"),
            (cls.CONSUMABLE.value, "consumable"),
            (cls.MISSED_RESERVATION.value, "missed_reservation"),
            (cls.STAFF_CHARGE.value, "staff_charge"),
            (cls.TRAINING.value, "training_session"),
            (cls.CUSTOM_CHARGE.value, "custom_charge"),
        )

    @classmethod
    def choices_except(cls, *billable_types):
        return [item for item in cls.choices() if BillableItemType(item[0]) not in billable_types]

    def is_time_type(self):
        return self in [
            BillableItemType.TOOL_USAGE,
            BillableItemType.AREA_ACCESS,
            BillableItemType.TRAINING,
            BillableItemType.STAFF_CHARGE,
            BillableItemType.MISSED_RESERVATION,
        ]

    def display_name(self):
        choices_as_dict = dict(self.choices())
        return choices_as_dict.get(self.value)

    def friendly_display_name(self):
        return self.display_name().replace("_", " ").capitalize()

    def category_name_for_item_type(self):
        return category_name_for_item_type(self)


class ProjectBillingDetails(BaseModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    category = models.ForeignKey(RateCategory, null=True, blank=True, on_delete=models.SET_NULL)
    project_name = models.CharField(
        null=True,
        blank=True,
        max_length=CHAR_FIELD_LARGE_LENGTH,
        help_text="The project name that will appear on the invoices. Leave blank to use NEMO project name",
    )
    contact_name = models.CharField(
        null=True,
        blank=True,
        max_length=CHAR_FIELD_MEDIUM_LENGTH,
        help_text="The contact name to use in the invoice email",
    )
    contact_phone = models.CharField(null=True, blank=True, max_length=40, help_text="The contact's phone number")
    contact_email = fields.MultiEmailField(
        null=True,
        blank=True,
        help_text="Email to send the invoice to. A comma-separated list can be used. Leave blank to use project managers/PIs emails",
    )
    expires_on = models.DateField(
        null=True, blank=True, help_text="Date after which this project will be automatically deactivated."
    )
    addressee = models.TextField(null=True, blank=True, help_text="The addressee details to be included in the invoice")
    institution = models.ForeignKey(
        "NEMO_billing.Institution",
        null=True,
        blank=True,
        help_text="The project institution",
        on_delete=models.SET_NULL,
    )
    department = models.ForeignKey(
        "NEMO_billing.Department", null=True, blank=True, help_text="The project department", on_delete=models.SET_NULL
    )
    staff_host = models.ForeignKey(User, null=True, blank=True, help_text="The project host", on_delete=models.SET_NULL)
    comments = models.TextField(null=True, blank=True)
    no_charge = models.BooleanField(
        default=False, help_text="Check this box if invoices should not be created for this project."
    )
    no_tax = models.BooleanField(default=False, help_text="Check this box if this project is tax exempt.")

    @property
    def name(self):
        return self.project_name if self.project_name else self.project.name

    def clean(self):
        if not self.category and RateCategory.objects.exists():
            raise ValidationError({"category": "You need to select a rate category for this project"})

    def email_to(self) -> List[str]:
        # return project PIs emails if not set here
        return self.contact_email if not self.email_empty() else [pi.email for pi in self.project.manager_set.all()]

    def email_empty(self):
        return not self.contact_email or not [email for email in self.contact_email if email]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Project details"


class InvoiceConfiguration(BaseModel):
    name = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH, unique=True, help_text="The name of this invoice configuration"
    )
    invoice_due_in = models.PositiveIntegerField(
        help_text="The default number of days invoices are due after", default=30
    )
    invoice_title = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH,
        default="Invoice",
        help_text="The title displayed on the first page of the invoice (e.g. Invoice/Statement/Quote)",
    )
    reminder_frequency = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=7,
        help_text="How often to send a reminder. Default value is 7, meaning every week after past due invoice",
    )
    email_from = models.EmailField(help_text="The email address used to send invoices and reminders")
    email_cc = fields.MultiEmailField(
        null=True, blank=True, help_text="Email to cc the invoice to. A comma-separated list can be used"
    )
    merchant_name = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH)
    merchant_details = models.TextField(
        null=True,
        blank=True,
        help_text="The merchant details to be included in the invoice (address, phone number etc.)",
    )
    merchant_logo = models.ImageField(null=True, blank=True, upload_to=get_merchant_logo_filename)
    terms = models.TextField(null=True, blank=True, help_text="Terms and conditions to be included in the invoice")

    currency = models.CharField(max_length=4, default="USD")
    currency_symbol = models.CharField(null=True, blank=True, max_length=4, default="$")

    tax = models.DecimalField(
        null=True, blank=True, decimal_places=3, max_digits=5, help_text="Tax in percent. For 20.5% enter 20.5"
    )
    tax_name = models.CharField(max_length=CHAR_FIELD_SMALL_LENGTH, null=True, blank=True, default="VAT")

    detailed_invoice = models.BooleanField(
        default=True, help_text="Check this box if customers should receive a detailed invoice."
    )
    hide_zero_charge = models.BooleanField(default=True, help_text="Hide charges with an amount equal to 0.")

    separate_tool_usage_charges = models.BooleanField(
        default=False, help_text="Check this box to display tool usage charges as a separate invoice category"
    )
    separate_area_access_charges = models.BooleanField(
        default=False, help_text="Check this box to display area access charges as a separate invoice category"
    )
    separate_staff_charges = models.BooleanField(
        default=False, help_text="Check this box to display staff charges as a separate invoice category"
    )
    separate_consumable_charges = models.BooleanField(
        default=False, help_text="Check this box to display supplies/material as a separate invoice category"
    )
    separate_missed_reservation_charges = models.BooleanField(
        default=False, help_text="Check this box to display missed reservation charges as a separate invoice category"
    )
    separate_training_charges = models.BooleanField(
        default=False, help_text="Check this box to display training charges as a separate invoice category"
    )
    separate_custom_charges = models.BooleanField(
        default=False, help_text="Check this box to display custom charges as a separate invoice category"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_help_initialized = False

    def tax_display(self):
        return f"{self.tax:.2f}"

    def tax_amount(self):
        return (self.tax or Decimal(0)) / Decimal(100)

    @property
    def rates_exist(self):
        if not self.rate_help_initialized:
            self.init_rate_help()
        return self._rates_exist

    @property
    def rates_types(self):
        if not self.rate_help_initialized:
            self.init_rate_help()
        return self._rates_types

    @property
    def all_rates(self):
        if not self.rate_help_initialized:
            self.init_rate_help()
        return self._all_rates

    def init_rate_help(self, extra_filter=Q()):
        # Call this to initiate a few helping rate items to basically cache them
        self._rates_types = {rate_type.type: rate_type for rate_type in RateType.objects.all()}
        self._rates_exist = RateCategory.objects.exists()
        self._all_rates = list(Rate.non_deleted().filter(extra_filter).select_related("type", "time", "category"))
        self.rate_help_initialized = True

    def __str__(self):
        return self.name

    @classmethod
    def first_or_default(cls):
        try:
            if cls.objects.exists():
                return cls.objects.first()
        except Exception as e:
            getLogger(__name__).warning(e)
        return cls(currency="", currency_symbol="")


class Invoice(BaseModel):
    invoice_number = models.CharField(
        null=False,
        blank=True,
        max_length=CHAR_FIELD_SMALL_LENGTH,
        unique=True,
        help_text="Leave blank to be assigned automatically",
    )
    start = models.DateTimeField()
    end = models.DateTimeField()

    configuration = models.ForeignKey(InvoiceConfiguration, on_delete=models.PROTECT)
    project_details = models.ForeignKey(ProjectBillingDetails, on_delete=models.PROTECT)

    due_date = models.DateField(blank=True, null=True)
    sent_date = models.DateTimeField(blank=True, null=True)
    last_sent_date = models.DateTimeField(blank=True, null=True)
    last_reminder_sent_date = models.DateTimeField(blank=True, null=True)
    reviewed_date = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User, blank=True, null=True, related_name="reviewed_invoice_set", on_delete=models.PROTECT
    )
    voided_date = models.DateTimeField(blank=True, null=True)
    voided_by = models.ForeignKey(
        User, blank=True, null=True, related_name="voided_invoice_set", on_delete=models.PROTECT
    )

    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_date = models.DateTimeField(auto_now_add=True)

    total_amount = models.DecimalField(decimal_places=2, max_digits=14)

    file = models.FileField(
        null=True, blank=True, max_length=CHAR_FIELD_MEDIUM_LENGTH, upload_to=get_invoice_document_filename
    )

    def generate_invoice_number(self, update: bool = False):
        from NEMO_billing.invoices.customization import InvoiceCustomization

        number_format = InvoiceCustomization.get("invoice_number_format")
        current_number = 0
        try:
            current_number = int(InvoiceCustomization.get("invoice_number_current"))
        except ValueError:
            pass
        current_number += 1
        if update:
            Customization.objects.update_or_create(
                name="invoice_number_current", defaults={"value": str(current_number)}
            )
        return number_format.format(current_number)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number(True)
        super().save(*args, **kwargs)

    def save_all(self, detail_items, summary_items):
        # Save invoice, detail items and summary items
        self.save()
        for detail_item in detail_items:
            detail_item.invoice = self
            detail_item.save(force_insert=True)
        for summary_item in summary_items:
            summary_item.invoice = self
            summary_item.save(force_insert=True)
        # We want to generate/render the invoice now and save the file so that it is set once and for all
        # (rather than generating it on the fly which would potentially use newer project info and config)
        # if an error rendering happens, the file will need to be regenerated
        self.render_and_save_file()

    def get_absolute_url(self):
        return reverse("view_invoice", kwargs={"invoice_id": self.id})

    def filename(self, extension=None):
        extension = f".{extension}" if extension else os.path.splitext(self.file.path)[1]
        return f"{slugify(self.invoice_number)}_{slugify(self.project_details.name)}{extension}"

    def filename_for_zip(self, extension=None):
        extension = f".{extension}" if extension else os.path.splitext(self.file.path)[1]
        return export_invoice_filename(self) + extension

    def render_and_save_file(self):
        from NEMO_billing.invoices.renderers import invoice_renderer_class

        content = invoice_renderer_class.render_invoice(self)
        content.seek(0)
        self.file = ContentFile(content.read(), "invoice." + invoice_renderer_class.get_file_extension())
        content.close()
        self.save(update_fields=["file"])

    def _email_invoice(self, template_name) -> bool:
        attachment = create_email_attachment(self.file, self.filename())
        sent = render_and_send_email(
            template_name,
            {"invoice": self},
            to=self.project_details.email_to(),
            from_email=self.configuration.email_from,
            cc=self.configuration.email_cc,
            attachments=[attachment],
        )
        return bool(sent)

    def send(self) -> bool:
        # Email the invoice. If it was already sent, don't change the due date
        if not self.voided_date and self.reviewed_date:
            self.last_sent_date = timezone.now()
            if not self.sent_date:
                self.sent_date = timezone.now()
                self.due_date = timezone.now() + timedelta(days=self.configuration.invoice_due_in)
            if self._email_invoice("invoices/email/email_send_invoice"):
                self.save()
                return True
        return False

    def send_reminder(self) -> bool:
        if self.sent_date:
            if self.total_payments_received() < self.total_amount:
                # Invoice hasn't been paid in full, reminder should be sent
                self.last_reminder_sent_date = timezone.now()
                if self._email_invoice("invoices/email/email_send_invoice_reminder"):
                    self.save()
                    return True
        return False

    def sorted_core_facilities(self, detail_items=None) -> List[str]:
        if detail_items:
            core_facilities = list({item.core_facility for item in detail_items})
        else:
            core_facilities = list(self.invoicedetailitem_set.values_list("core_facility", flat=True).distinct())
        core_facilities.sort(key=lambda x: x if x else "", reverse=True)
        return core_facilities

    def summary_dict(self) -> Dict[str, List]:
        summary_details = {}
        for core_facility in self.sorted_core_facilities():
            core_facility_details = self.invoicesummaryitem_set.filter(core_facility=core_facility)
            if self.configuration.hide_zero_charge:
                core_facility_details = core_facility_details.exclude(amount=0)
            summary_details.setdefault(core_facility, core_facility_details)
        details = self.invoicesummaryitem_set.filter(core_facility=None)
        if self.configuration.hide_zero_charge:
            details = details.exclude(amount=0)
        summary_details.setdefault(None, details)
        return summary_details

    def details_dict(self) -> Dict[str, Dict[str, List]]:
        details = {}
        for core_facility in self.sorted_core_facilities():
            details.setdefault(core_facility, {})
            core_facility_items = details.get(core_facility)
            core_facility_items.setdefault("tool_usage", self.tool_usage_details(core_facility=core_facility))
            core_facility_items.setdefault("area_access", self.area_access_details(core_facility=core_facility))
            core_facility_items.setdefault("staff_charges", self.staff_charge_details(core_facility=core_facility))
            core_facility_items.setdefault(
                "consumable_withdrawals", self.consumable_withdrawal_details(core_facility=core_facility)
            )
            core_facility_items.setdefault("trainings", self.training_details(core_facility=core_facility))
            core_facility_items.setdefault(
                "missed_reservations", self.missed_reservation_details(core_facility=core_facility)
            )
            core_facility_items.setdefault("custom_charges", self.custom_charges_details(core_facility=core_facility))
        return details

    def invoice_details(self):
        details = self.invoicedetailitem_set.all()
        if self.configuration.hide_zero_charge:
            details = details.exclude(amount=0)
        return details

    def tool_usage_details(self, core_facility: str):
        return (
            self.invoice_details()
            .filter(core_facility=core_facility, item_type=BillableItemType.TOOL_USAGE.value)
            .order_by("start")
        )

    def area_access_details(self, core_facility: str):
        return (
            self.invoice_details()
            .filter(core_facility=core_facility, item_type=BillableItemType.AREA_ACCESS.value)
            .order_by("start")
        )

    def staff_charge_details(self, core_facility: str):
        return self.invoice_details().filter(core_facility=core_facility, item_type=BillableItemType.STAFF_CHARGE.value)

    def consumable_withdrawal_details(self, core_facility: str):
        return (
            self.invoice_details()
            .filter(core_facility=core_facility, item_type=BillableItemType.CONSUMABLE.value)
            .order_by("start")
        )

    def training_details(self, core_facility: str):
        return (
            self.invoice_details()
            .filter(core_facility=core_facility, item_type=BillableItemType.TRAINING.value)
            .order_by("start")
        )

    def missed_reservation_details(self, core_facility: str):
        return (
            self.invoice_details()
            .filter(core_facility=core_facility, item_type=BillableItemType.MISSED_RESERVATION.value)
            .order_by("start")
        )

    def custom_charges_details(self, core_facility: str):
        return (
            self.invoice_details()
            .filter(core_facility=core_facility, item_type=BillableItemType.CUSTOM_CHARGE.value)
            .order_by("start")
        )

    def total_amount_display(self) -> str:
        return display_amount(self.total_amount, self.configuration)

    def total_payments_received(self) -> Decimal:
        return self.invoicepayment_set.aggregate(
            total_received=Coalesce(
                Sum(Case(When(payment_received__isnull=False, then="amount"), default=Decimal(0))), Decimal(0)
            )
        )["total_received"]

    def total_payments_processed(self) -> Decimal:
        return self.invoicepayment_set.aggregate(
            total_processed=Coalesce(
                Sum(Case(When(payment_processed__isnull=False, then="amount"), default=Decimal(0))), Decimal(0)
            )
        )["total_processed"]

    def total_outstanding_amount(self) -> Decimal:
        return self.total_amount - self.total_payments_received()

    def total_outstanding_display(self) -> str:
        return display_amount(self.total_outstanding_amount(), self.configuration)

    def total_payments_display(self) -> str:
        pending_display = f" ({display_amount(self.total_payments_received()-self.total_payments_processed(), self.configuration)} pending)"
        return f"{self.total_outstanding_display()}{pending_display}"

    def mark_as_paid_in_full(self, user):
        outstanding = self.total_outstanding_amount()
        if outstanding > 0:
            self.record_payment(user, outstanding, timezone.now(), timezone.now())

    def record_payment(self, user: User, amount: Decimal, received=None, processed=None, note=None) -> InvoicePayment:
        return InvoicePayment.objects.create(
            invoice=self,
            created_by=user,
            updated_by=user,
            payment_received=received,
            payment_processed=processed,
            amount=amount,
            note=note,
        )

    def tax_display(self) -> str:
        return display_amount(
            self.invoicesummaryitem_set.aggregate(
                total_tax=Coalesce(
                    Sum(
                        Case(
                            When(summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.TAX, then="amount"),
                            default=Decimal(0),
                        )
                    ),
                    Decimal(0),
                )
            )["total_tax"],
            self.configuration,
        )

    def __str__(self):
        created_date = f" ({self.created_date.date()})" if self.created_date else ""
        return f"{self.invoice_number}: {self.project_details.name}{created_date}"

    class Meta:
        ordering = ["-created_date", "-invoice_number"]


class InvoiceDetailItem(BaseModel):
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    core_facility = models.CharField(null=True, blank=True, max_length=CHAR_FIELD_MEDIUM_LENGTH)
    item_type = models.IntegerField(choices=BillableItemType.choices())
    name = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH)
    quantity = models.DecimalField(decimal_places=2, max_digits=8)
    start = models.DateTimeField()
    end = models.DateTimeField()
    user = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH)
    rate = models.CharField(null=True, blank=True, max_length=CHAR_FIELD_SMALL_LENGTH)
    amount = models.DecimalField(decimal_places=2, max_digits=14)
    discount = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=14)
    waived = models.BooleanField(default=False)

    def quantity_display(self):
        if self.item_type and BillableItemType(self.item_type).is_time_type():
            return f"{self.quantity:.2f} min"
        else:
            return f"{self.quantity:.2f}"

    def amount_display(self):
        amount = display_amount(self.amount, self.invoice.configuration)
        return f"{amount}{' (waived)' if self.waived else ''}"

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class InvoiceSummaryItem(BaseModel):
    class InvoiceSummaryItemType(object):
        ITEM = 1  # Any billable summary item
        SUBTOTAL = 2  # Facility subtotal (sum of billable summary item minus discounts)
        DISCOUNT_SUBTOTAL = 3  # Facility amount for discount (only used to calculate future accumulation discounts)
        DISCOUNT = 4  # Facility discount
        TAX = 5  # Tax
        OTHER = 6  # Other
        FUND = 7  # Other
        choices = (
            (ITEM, "item"),
            (SUBTOTAL, "sub_total"),
            (DISCOUNT_SUBTOTAL, "discount_sub_total"),
            (DISCOUNT, "discount"),
            (TAX, "tax"),
            (OTHER, "other"),
            (FUND, "fund"),
        )

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    summary_item_type = models.IntegerField(choices=InvoiceSummaryItemType.choices)
    item_type = models.IntegerField(null=True, blank=True, choices=BillableItemType.choices())
    core_facility = models.CharField(null=True, blank=True, max_length=CHAR_FIELD_MEDIUM_LENGTH)
    name = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH)
    details = models.CharField(null=True, blank=True, max_length=CHAR_FIELD_SMALL_LENGTH)
    amount = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=14)

    def amount_display(self):
        return display_amount(self.amount, self.invoice.configuration)

    def category_name_for_item_type(self):
        return category_name_for_item_type(self.item_type)


class InvoicePayment(BaseModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    payment_received = models.DateField(help_text="Date when payment was received")
    payment_processed = models.DateField(null=True, blank=True, help_text="Date when payment was processed")
    amount = models.DecimalField(decimal_places=2, max_digits=14, help_text="Amount received")
    note = models.CharField(null=True, blank=True, max_length=CHAR_FIELD_MEDIUM_LENGTH, help_text="Payment note")
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="payment_created_by_set", on_delete=models.PROTECT)
    updated_date = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name="payment_updated_by_set", on_delete=models.PROTECT)

    def amount_display(self):
        return display_amount(self.amount, self.invoice.configuration)

    def __str__(self):
        return f"Payment for invoice {self.invoice.invoice_number}"

    class Meta:
        ordering = ["-payment_received"]
