from NEMO.admin import AtLeastOneRequiredInlineFormSet
from NEMO.utilities import format_datetime
from django import forms
from django.contrib.admin import ModelAdmin, TabularInline, display, register, widgets
from django.utils.safestring import mark_safe

from NEMO_billing.cap_discount.customization import CAPDiscountCustomization
from NEMO_billing.cap_discount.models import CAPDiscount, CAPDiscountAmount, CAPDiscountConfiguration, CAPDiscountTier
from NEMO_billing.invoices.models import BillableItemType
from NEMO_billing.utilities import IntMultipleChoiceField, disable_form_field


class CAPDiscountAmountInline(TabularInline):
    model = CAPDiscountAmount
    readonly_fields = ("new_charges",)
    extra = 1


class CAPDiscountTierAdminFormset(AtLeastOneRequiredInlineFormSet):
    pass


class CAPDiscountTierInline(TabularInline):
    model = CAPDiscountTier
    formset = CAPDiscountTierAdminFormset
    extra = 1
    min_num = 1

    def __init__(self, parent_model, admin_site):
        if parent_model == CAPDiscount:
            self.exclude = ["cap_discount_configuration"]
        else:
            self.exclude = ["cap_discount"]
        super().__init__(parent_model, admin_site)


class CAPDiscountConfigurationForm(forms.ModelForm):
    charge_types = IntMultipleChoiceField(
        choices=BillableItemType.choices(),
        required=True,
        widget=widgets.FilteredSelectMultiple(verbose_name="Types", is_stacked=False),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("instance"):
            for field_name in ["rate_category", "split_by_user"]:
                disable_form_field(self, field_name)
        self.fields["charge_types"].initial = CAPDiscountCustomization.get("cap_billing_default_billable_types")
        if "reset_interval" in self.fields:
            self.fields["reset_interval"].initial = CAPDiscountCustomization.get("cap_billing_default_interval")
        if "reset_frequency" in self.fields:
            self.fields["reset_frequency"].initial = CAPDiscountCustomization.get("cap_billing_default_frequency")

    def _save_m2m(self):
        super()._save_m2m()
        # This is an edge case when first saving a model instance and no core_facilities are set
        # It will not trigger our signal (m2m_changed) for checking uniqueness unless we manually call clear
        if not self.instance.core_facilities.exists():
            self.instance.core_facilities.clear()

    class Meta:
        model = CAPDiscountConfiguration
        fields = "__all__"


class CAPDiscountForm(forms.ModelForm):
    charge_types = IntMultipleChoiceField(
        choices=BillableItemType.choices(),
        required=True,
        widget=widgets.FilteredSelectMultiple(verbose_name="Types", is_stacked=False),
    )

    class Meta:
        model = CAPDiscount
        fields = "__all__"


@register(CAPDiscount)
class CAPDiscountAdmin(ModelAdmin):
    form = CAPDiscountForm
    inlines = [CAPDiscountTierInline, CAPDiscountAmountInline]
    list_display = (
        "id",
        "account",
        "get_core_facilities",
        "rate_category",
        "user",
        "current_amount",
        "discount_display",
        "reset_frequency_display",
        "next_reset_display",
    )
    list_filter = ("configuration__core_facilities", "configuration__rate_category", "account", "user")

    @display(ordering="configuration__core_facilities", description="Core facilities")
    def get_core_facilities(self, cap_discount: CAPDiscount):
        return mark_safe("<br>".join(cap_discount.configuration.core_facility_names))

    @display(ordering="configuration__rate_category", description="Rate category")
    def rate_category(self, cap_discount: CAPDiscount):
        return cap_discount.configuration.rate_category

    @display(description="Reset frequency")
    def reset_frequency_display(self, cap_discount: CAPDiscount):
        return cap_discount.get_recurrence_display() or "-"

    @display(ordering="capdiscounttier", description="Discount")
    def discount_display(self, cap_discount: CAPDiscount):
        return mark_safe("<br>".join(str(tier) for tier in cap_discount.capdiscounttier_set.all()))

    @display(description="Next reset")
    def next_reset_display(self, cap_discount: CAPDiscount):
        return format_datetime(cap_discount.next_reset(), "F Y") if cap_discount.next_reset() else "-"

    @display(description="Current amount")
    def current_amount(self, cap_discount: CAPDiscount):
        return cap_discount.latest_amount().end


@register(CAPDiscountConfiguration)
class CAPDiscountConfigurationAdmin(ModelAdmin):
    form = CAPDiscountConfigurationForm
    inlines = [CAPDiscountTierInline]
    list_display = (
        "id",
        "get_core_facilities",
        "rate_category",
        "discount_display",
        "reset_frequency_display",
    )
    list_filter = ("core_facilities", "rate_category")
    filter_horizontal = ["core_facilities"]

    @display(description="Core facilities", ordering="core_facilities")
    def get_core_facilities(self, config: CAPDiscountConfiguration):
        return mark_safe("<br>".join(config.core_facility_names))

    @display(description="Reset frequency")
    def reset_frequency_display(self, config: CAPDiscountConfiguration):
        return config.get_recurrence_interval_display() or "-"

    @display(ordering="capdiscounttier", description="Discount")
    def discount_display(self, config: CAPDiscountConfiguration):
        return mark_safe("<br>".join(str(tier) for tier in config.capdiscounttier_set.all()))
