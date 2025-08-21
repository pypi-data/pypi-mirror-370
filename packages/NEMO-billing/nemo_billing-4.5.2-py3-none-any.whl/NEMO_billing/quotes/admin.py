from NEMO.mixins import ModelAdminRedirectMixin
from NEMO.utilities import new_model_copy
from django.contrib import admin
from django.contrib.admin import register
from django.utils.safestring import mark_safe

from NEMO_billing.quotes.models import Quote, QuoteConfiguration, QuoteItem
from NEMO_billing.quotes.utilities import delete_approval_request_notification


def clone_configuration(configuration: QuoteConfiguration):
    """
    Create a clone of selected configurations and save them.

    :param configuration:
    :return: Newly cloned configuration
    """
    new_configuration = new_model_copy(configuration)
    new_configuration.name = f"Copy of {configuration.name}"
    new_configuration.save()

    return new_configuration


@admin.action(description="Clone selected Configurations")
def clone_configurations(modeladmin, request, queryset):
    for configuration in queryset.all():
        clone_configuration(configuration)


@register(QuoteConfiguration)
class QuoteConfigurationAdmin(ModelAdminRedirectMixin, admin.ModelAdmin):
    list_display = ("id", "name", "merchant_name", "currency", "get_create_permission", "get_approval_permissions")
    ordering = ("name",)
    actions = (clone_configurations,)
    fieldsets = (
        (None, {"fields": ("name", "expiration_in_days")}),
        (
            "Quote Number template",
            {"fields": ("quote_numbering_template", "current_quote_number")},
        ),
        ("Communication", {"fields": ("email_from", "email_cc")}),
        ("Permissions", {"fields": ("create_permissions", "approval_permissions")}),
        ("Merchant info", {"fields": ("merchant_name", "merchant_details", "merchant_logo", "terms")}),
        ("Currency", {"fields": ("currency", "currency_symbol")}),
        ("Tax", {"fields": ("tax_name", "tax")}),
    )

    @admin.display(description="Create permissions", ordering="create_permissions")
    def get_create_permission(self, obj: QuoteConfiguration):
        return mark_safe(
            "<br>".join(
                str(obj.get_create_permissions_field().role_display(role_str, admin_display=True))
                for role_str in obj.create_permissions
            )
        )

    @admin.display(description="Approval permissions", ordering="approval_permissions")
    def get_approval_permissions(self, obj: QuoteConfiguration):
        return mark_safe(
            "<br>".join(
                str(obj.get_approval_permissions_field().role_display(role_str, admin_display=True))
                for role_str in obj.approval_permissions
            )
        )


@admin.action(description="Unpublish selected quotes")
def unpublish_quote(modeladmin, request, queryset):
    quotes = queryset.filter(status=Quote.Status.PUBLISHED)
    quotes.update(
        status=Quote.Status.DRAFT,
        approved_by=None,
        expiration_date=None,
        published_date=None,
        file=None,
        file_access_token=None,
    )
    for quote in quotes:
        delete_approval_request_notification(quote)


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    inlines = [QuoteItemInline]
    list_display = ("id", "name", "quote_number", "status", "configuration")
    actions = [unpublish_quote]
    ordering = ("name",)
    list_filter = ("configuration", "status")
    fieldsets = (("Quote Editable Information", {"fields": ("name", "quote_number", "project", "users", "emails")}),)

    def delete_queryset(self, request, queryset):
        # forcing it to go through the model delete so the notifications are deleted as well
        for quote in queryset:
            quote.delete()
