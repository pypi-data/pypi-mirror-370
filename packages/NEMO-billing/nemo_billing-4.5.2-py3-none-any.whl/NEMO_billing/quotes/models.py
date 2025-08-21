import os
import secrets
from datetime import datetime, timedelta
from logging import getLogger

from NEMO.constants import CHAR_FIELD_MAXIMUM_LENGTH, CHAR_FIELD_MEDIUM_LENGTH, CHAR_FIELD_SMALL_LENGTH
from NEMO.fields import MultiEmailField, MultiRoleGroupPermissionChoiceField
from NEMO.models import BaseModel, Project, User
from NEMO.utilities import get_full_url, update_media_file_on_model_update
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.dispatch import receiver
from django.template import Template, Context
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from NEMO_billing.rates.models import Rate

quotes_logger = getLogger(__name__)


def get_quote_document_filename(quote, filename):
    quote_name = slugify(quote.name)
    now = datetime.now()
    generated_date = now.strftime("%Y-%m-%d_%H-%M-%S")
    year = now.strftime("%Y")
    ext = os.path.splitext(filename)[1]
    return f"quotes/{year}/{slugify(quote.quote_number)}_{quote_name}_{generated_date}{ext}"


class QuoteConfiguration(BaseModel):
    name = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH, unique=True, help_text="The name of this quote configuration"
    )
    expiration_in_days = models.PositiveIntegerField(
        help_text="The default number of days quotes are valid for once published", default=30
    )
    quote_numbering_template = models.CharField(
        default="{{ number|stringformat:'04d' }}",
        max_length=CHAR_FIELD_MEDIUM_LENGTH,
        help_text="Django template for quote numbering. Available variables: date_created, number",
    )
    current_quote_number = models.PositiveIntegerField(
        default=0,
        help_text="The current quote number used for this configuration. This is automatically incremented when a new quote is created.",
    )
    email_from = models.EmailField(help_text="The email address used to send quotes")
    email_cc = MultiEmailField(
        null=True, blank=True, help_text="Email to cc the quote to. A comma-separated list can be used"
    )
    merchant_name = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH)
    merchant_details = models.TextField(
        null=True,
        blank=True,
        help_text="The merchant details to be included in the quote (address, phone number etc.)",
    )
    merchant_logo = models.ImageField(null=True, blank=True, upload_to="quote_logos")
    terms = models.TextField(null=True, blank=True, help_text="Terms and conditions to be included in the quote")

    currency = models.CharField(max_length=4, default="USD")
    currency_symbol = models.CharField(null=True, blank=True, max_length=4, default="$")

    tax = models.DecimalField(
        null=True, blank=True, decimal_places=3, max_digits=5, help_text="Tax in percent. For 20.5% enter 20.5"
    )
    tax_name = models.CharField(max_length=CHAR_FIELD_SMALL_LENGTH, null=True, blank=True, default="VAT")
    create_permissions = MultiRoleGroupPermissionChoiceField(
        groups=True,
        help_text="The roles/groups required for users to create this type of quote",
    )
    approval_permissions = MultiRoleGroupPermissionChoiceField(
        null=True,
        blank=True,
        groups=True,
        help_text="The roles/groups required for users to approve this type of quote",
    )

    @classmethod
    def get_approval_permissions_field(cls) -> MultiRoleGroupPermissionChoiceField:
        return cls._meta.get_field("approval_permissions")

    @classmethod
    def get_create_permissions_field(cls) -> MultiRoleGroupPermissionChoiceField:
        return cls._meta.get_field("create_permissions")

    def can_user_create(self, user) -> bool:
        return self.get_create_permissions_field().has_user_roles(self.create_permissions, user)

    def can_user_approve(self, user) -> bool:
        return self.get_approval_permissions_field().has_user_roles(self.approval_permissions, user)

    def get_all_reviewers(self):
        if not self.approval_permissions:
            return User.objects.none()

        user_sets = [self.get_approval_permissions_field().users_with_role(role) for role in self.approval_permissions]
        if len(user_sets) == 0:
            return User.objects.none()

        combined = user_sets[0]
        for qs in user_sets[1:]:
            combined |= qs
        return combined

    def __str__(self):
        return f"{self.name}"


class Quote(BaseModel):
    class Status(object):
        DRAFT = 0
        PENDING_APPROVAL = 1
        PUBLISHED = 2
        Choices = (
            (DRAFT, "Draft"),
            (PENDING_APPROVAL, "Pending Approval"),
            (PUBLISHED, "Published"),
        )

    name = models.CharField(
        null=False,
        blank=False,
        max_length=CHAR_FIELD_SMALL_LENGTH,
        help_text="Name of the quote",
    )
    quote_number = models.CharField(
        null=True,
        blank=True,
        max_length=CHAR_FIELD_MEDIUM_LENGTH,
        help_text="Quote number. This is automatically generated based on the quote configuration",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Project associated with this quote",
    )
    configuration = models.ForeignKey(
        QuoteConfiguration,
        on_delete=models.PROTECT,
        help_text="Configuration for this quote",
    )
    users = models.ManyToManyField(User, blank=True, help_text="Users associated with this quote")
    emails = MultiEmailField(
        null=True, blank=True, help_text="Email addresses to send this quote to. A comma-separated list can be used"
    )
    expiration_date = models.DateField(null=True, blank=True, help_text="Date when this quote expires")
    creator = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="quotes_created", help_text="User who created this quote"
    )
    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="quotes_approved",
        help_text="User who approved or published this quote",
    )
    created_date = models.DateTimeField(auto_now_add=True, help_text="Date and time when this quote was created")
    updated_date = models.DateTimeField(auto_now=True, help_text="Date and time when this quote was last updated")
    published_date = models.DateTimeField(
        null=True, blank=True, help_text="Date and time when this quote was published"
    )
    last_emails_sent_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the last emails were sent for this quote",
    )
    status = models.IntegerField(
        choices=Status.Choices,
        null=False,
        blank=False,
        default=Status.DRAFT,
        help_text="Current status of the quote",
    )
    file = models.FileField(
        null=True, blank=True, max_length=CHAR_FIELD_MEDIUM_LENGTH, upload_to=get_quote_document_filename
    )
    file_access_token = models.CharField(
        null=True,
        blank=True,
        max_length=CHAR_FIELD_MAXIMUM_LENGTH,
        help_text="A random token used to access the quote file without authentication",
    )
    add_tax = models.BooleanField(
        default=False,
        help_text="Whether to add tax to the total amount of this quote",
    )

    @property
    def items(self):
        return self.quoteitem_set.all()

    @property
    def tax_amount(self):
        if self.configuration.tax and self.add_tax:
            return self.items_sum_total() * (self.configuration.tax / 100)
        return 0

    @property
    def tax_amount_display(self):
        return f"{self.configuration.currency_symbol}{self.tax_amount:.2f}  {self.configuration.currency}"

    def items_sum_total(self):
        return sum(item.total for item in self.items)

    @property
    def tax_display(self):
        if self.configuration.tax and self.add_tax:
            return f"{self.configuration.tax:.2f}%"
        return ""

    @property
    def total(self):
        return self.items_sum_total() + self.tax_amount

    @property
    def total_display(self):
        return f"{self.configuration.currency_symbol}{self.total:.2f} {self.configuration.currency}"

    @property
    def is_published(self) -> bool:
        return self.status == self.Status.PUBLISHED

    @property
    def is_pending_approval(self) -> bool:
        return self.status == self.Status.PENDING_APPROVAL

    @property
    def is_draft(self) -> bool:
        return self.status == self.Status.DRAFT

    @property
    def is_expired(self) -> bool:
        return self.expiration_date is not None and self.expiration_date < timezone.now().date()

    def can_edit_quote(self, user: User) -> bool:
        return self.creator == user

    def can_approve_quote(self, user: User) -> bool:
        return self.configuration.can_user_approve(user)

    def get_access_url(self):
        if self.file and self.file_access_token:
            url = get_full_url(reverse("public_quote_view", kwargs={"quote_id": self.id}))
            return f"{url}?token={self.file_access_token}"
        return None

    def permissions(self, user: User):
        requires_approval = bool(self.configuration.approval_permissions)
        user_can_edit = self.can_edit_quote(user)
        user_can_approve = self.can_approve_quote(user)
        can_edit = user_can_edit and self.is_draft
        can_edit_metadata = user_can_edit
        can_approve = user_can_approve and self.is_pending_approval
        can_send_emails = self.is_published and (user_can_edit or self.approved_by == user)
        return {
            "can_edit_metadata": can_edit_metadata,
            "can_approve": can_approve,
            "can_edit": can_edit,
            "requires_approval": requires_approval,
            "user_can_edit": user_can_edit,
            "can_send_emails": can_send_emails,
        }

    def publish(self, user: User):
        self.status = self.Status.PUBLISHED
        self.expiration_date = timezone.now().date() + timedelta(days=self.configuration.expiration_in_days)
        self.published_date = timezone.now()
        self.approved_by = user
        self.file = self.render_file()
        self.file_access_token = secrets.token_urlsafe()
        self.save()

    def submit_for_approval(self):
        self.status = self.Status.PENDING_APPROVAL
        self.save()

    def deny(self):
        self.status = self.Status.DRAFT
        self.save()

    def render_and_save(self):
        if self.is_published:
            self.file = self.render_file()
            self.save()

    def render_file(self):
        from NEMO_billing.quotes.renderers import quote_renderer_class

        content = quote_renderer_class.render(self)
        content.seek(0)
        content_file = ContentFile(content.read(), "quote." + quote_renderer_class.get_file_extension())
        content.close()
        return content_file

    def get_all_recipients(self):
        emails = []

        if self.users:
            for user in self.users.all():
                if user.email:
                    emails.append(user.email)

        if self.emails:
            for email in self.emails:
                emails.append(email)

        return emails

    def save(self, *args, **kwargs):
        if not self.quote_number:
            self.quote_number = self.generate_quote_number(True)
        super().save(*args, **kwargs)

    def generate_quote_number(self, update: bool = False):
        quote_number_template = self.configuration.quote_numbering_template
        current_number = self.configuration.current_quote_number
        try:
            template = Template(quote_number_template)
            date_created = self.created_date.date() if self.created_date else timezone.now().date()
            context = Context({"date_created": date_created, "number": current_number})
            quote_number = template.render(context)
            if update:
                self.configuration.current_quote_number = current_number + 1
                self.configuration.save()
            return quote_number
        except Exception:
            quotes_logger.warning("Error generating quote number", exc_info=True)
            return None

    def delete(self, *args, **kwargs):
        from NEMO_billing.quotes.utilities import delete_approval_request_notification

        delete_approval_request_notification(self)
        super().delete(*args, **kwargs)

    def clean(self):
        errors = {}

        if self.status == self.Status.PUBLISHED:
            if not self.published_date:
                errors["published_date"] = "Published quotes require a publication date."
            if not self.approved_by:
                errors["approved_by"] = "Published quotes require an approver."
            if not self.file:
                errors["file"] = "Published quotes require a document file."
            if not self.file_access_token:
                errors["file_access_token"] = "Published quotes require a file access token."
            if not self.expiration_date:
                errors["expiration_date"] = "Published quotes require an expiration date."
            elif self.expiration_date <= timezone.now().date():
                errors["expiration_date"] = "The expiration date for a published quote must be in the future."
        if self.status == self.Status.PENDING_APPROVAL:
            if self.approved_by:
                errors["approved_by"] = "Quotes waiting for approval must not have an approver."
            if self.published_date:
                errors["published_date"] = "Quotes waiting for approval must not have a publication date."
            if self.file:
                errors["file"] = "Quotes waiting for approval must not have a document file."
            if self.file_access_token:
                errors["file_access_token"] = "Quotes waiting for approval must not have a file access token."
        if self.status == self.Status.DRAFT:
            if self.approved_by:
                errors["approved_by"] = "Draft quotes must not have an approver."
            if self.published_date:
                errors["published_date"] = "Draft quotes must not have a publication date."
            if self.file:
                errors["file"] = "Draft quotes must not have a document file."
            if self.file_access_token:
                errors["file_access_token"] = "Draft quotes must not have a file access token."

        if errors:
            raise ValidationError(errors)


class QuoteItem(BaseModel):
    class AmountType(object):
        NOT_APPLICABLE = 0
        FLAT = 1
        HOURLY = 2
        DAILY = 3
        Choices = (
            (NOT_APPLICABLE, "N/A"),
            (FLAT, "Flat"),
            (HOURLY, "Hourly"),
            (DAILY, "Daily"),
        )

    quantity = models.DecimalField(
        null=False,
        blank=False,
        max_digits=8,
        default=1,
        decimal_places=0,
        help_text="Quantity of the item",
    )
    amount = models.DecimalField(
        null=False, blank=False, decimal_places=2, max_digits=8, help_text="Amount for this item"
    )
    minimum_charge = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=8, help_text="Minimum amount for this item"
    )
    description = models.CharField(
        null=False, blank=False, max_length=CHAR_FIELD_MEDIUM_LENGTH, help_text="Description for this item"
    )
    rate_type = models.IntegerField(
        choices=AmountType.Choices,
        null=False,
        blank=False,
        default=AmountType.NOT_APPLICABLE,
        help_text="Rate type (N/A, Flat, Hourly, Daily) for this item",
    )
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)

    @property
    def display_rate(self):
        amount = f"{self.amount:.2f}" if self.amount is not None else "N/A"
        if self.rate_type == self.AmountType.FLAT:
            amount = f"flat {amount}"
        elif self.rate_type == self.AmountType.HOURLY:
            amount = f"{amount}/hr"
        elif self.rate_type == self.AmountType.DAILY:
            amount = f"daily {amount}"
        minimum = f" ({self.minimum_charge:.2f} minimum)" if self.minimum_charge else ""
        return f"{amount}{minimum}"

    @property
    def total(self):
        amount = self.amount
        minimum_charge = self.minimum_charge if self.minimum_charge else 0
        return max(amount * self.quantity, minimum_charge)

    @property
    def total_display(self):
        return f"{self.quote.configuration.currency_symbol}{self.total:.2f} {self.quote.configuration.currency}"

    def clean(self):
        errors = {}

        if self.quantity <= 0:
            errors["quantity"] = "Quantity must be greater than zero."

        if self.description and self.description.strip() == "":
            errors["description"] = "Description cannot be empty."

        if self.minimum_charge is not None and self.minimum_charge < 0:
            errors["minimum_charge"] = "Minimum charge cannot be negative."

        if errors:
            raise ValidationError(errors)


@receiver(models.signals.post_delete, sender=Quote)
def auto_delete_file_on_quote_delete(sender, instance: Quote, **kwargs):
    if instance.file:
        instance.file.delete(False)


@receiver(models.signals.pre_save, sender=Quote)
def auto_update_file_on_quote_change(sender, instance: Quote, **kwargs):
    return update_media_file_on_model_update(instance, "file")
