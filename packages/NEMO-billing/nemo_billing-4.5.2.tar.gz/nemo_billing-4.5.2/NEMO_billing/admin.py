from copy import deepcopy
from typing import Optional

from NEMO.admin import AreaAdmin, AreaAdminForm, ConsumableAdmin, StaffChargeAdmin, ToolAdmin, ToolAdminForm
from NEMO.models import Area, Consumable, StaffCharge, Tool
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import register, widgets
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError
from django.db.models import Q

from NEMO_billing.customization import BillingCustomization
from NEMO_billing.invoices.models import BillableItemType
from NEMO_billing.models import (
    CoreFacility,
    CoreRelationship,
    CustomCharge,
    Department,
    Institution,
    InstitutionType,
    ProjectBillingHardCap,
)
from NEMO_billing.templatetags.billing_tags import cap_discount_installed
from NEMO_billing.utilities import IntMultipleChoiceField, hide_form_field

STATES = [
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AS", "American Samoa"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("DC", "District of Columbia"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("GU", "Guam"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("MP", "Northern Mariana Islands"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("PR", "Puerto Rico"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VI", "Virgin Islands"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming"),
]


def changed_or_added(change, original_set, current_set):
    # If the model object is being changed then we can get the list of previous members.
    if change:
        original_members = set(original_set)
    else:  # The model object is being created (instead of changed) so we can assume there are no members (initially).
        original_members = set()
    current_members = set(current_set)
    added_members = []
    removed_members = []

    # Log membership changes if they occurred.
    symmetric_difference = original_members ^ current_members
    if symmetric_difference:
        if change:  # the members have changed, so find out what was added and removed...
            # We can see the previous members of the object model by looking it up
            # in the database because the member list hasn't been committed yet.
            added_members = set(current_members) - set(original_members)
            removed_members = set(original_members) - set(current_members)

        else:  # a model object is being created (instead of changed) so we can assume all the members are new...
            added_members = current_set
    return added_members, removed_members


def save_all_core_facility_relationships(
    current_items, original_items, core_facility: CoreFacility, field: str, change
):
    added_items, removed_items = changed_or_added(change, original_items, current_items)
    for item in added_items:
        save_or_delete_core_facility(item, core_facility, field)
    for item in removed_items:
        save_or_delete_core_facility(item, None, field)


def save_or_delete_core_facility(obj, core_facility: Optional[CoreFacility], field):
    has_core_relationship = hasattr(obj, "core_rel")
    if core_facility:
        if not has_core_relationship:
            obj.core_rel = CoreRelationship()
        obj.core_rel.core_facility = core_facility
        setattr(obj.core_rel, field, obj)
        obj.core_rel.save()
    elif not core_facility and has_core_relationship:
        obj.core_rel.delete()


class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, values_only=False, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self._values_only = values_only
        self.attrs.update({"list": "list__{}".format(self._name)})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__{}">'.format(self._name)
        for item in self._list:
            value = item[0] if not self._values_only else item[1]
            data_list += '<option value="{}">{}</option>'.format(value, item[1])
        data_list += "</datalist>"

        return text_html + data_list


class InstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = "__all__"
        widgets = {"state": ListTextWidget(data_list=STATES, name="state_list", values_only=True)}


@register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ["name", "institution_type", "state", "get_country_display", "zip_code"]
    form = InstitutionForm


class CoreFacilityAdminForm(forms.ModelForm):
    class Meta:
        model = CoreFacility
        fields = "__all__"

    core_facility_tools = forms.ModelMultipleChoiceField(
        queryset=Tool.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name="Core facility tools", is_stacked=False),
    )
    core_facility_areas = forms.ModelMultipleChoiceField(
        queryset=Area.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name="Core facility areas", is_stacked=False),
    )
    core_facility_consumables = forms.ModelMultipleChoiceField(
        queryset=Consumable.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name="Core facility consumable", is_stacked=False),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We are filtering out already set tools, areas and consumables
        no_facility_filter = Q(core_rel__isnull=True)
        if "external_id" in self.fields:
            self.fields["external_id"].label = BillingCustomization.get("billing_core_facility_external_id_name")

        # Exclude children tools since their core facility is their parent's
        if "core_facility_tools" in self.fields:
            tool_filter = Q()
            if self.instance.pk:
                tool_filter = Q(core_rel__in=self.instance.corerelationship_set.filter(tool__isnull=False))
            self.fields["core_facility_tools"].queryset = Tool.objects.filter(tool_filter | no_facility_filter).exclude(
                parent_tool__isnull=False
            )
            if self.instance.pk:
                self.fields["core_facility_tools"].initial = Tool.objects.filter(tool_filter)
        if "core_facility_areas" in self.fields:
            area_filter = Q()
            if self.instance.pk:
                area_filter = Q(core_rel__in=self.instance.corerelationship_set.filter(area__isnull=False))
            self.fields["core_facility_areas"].queryset = Area.objects.filter(area_filter | no_facility_filter)
            if self.instance.pk:
                self.fields["core_facility_areas"].initial = Area.objects.filter(area_filter)
        if "core_facility_consumables" in self.fields:
            consumable_filter = Q()
            if self.instance.pk:
                consumable_filter = Q(core_rel__in=self.instance.corerelationship_set.filter(consumable__isnull=False))
            self.fields["core_facility_consumables"].queryset = Consumable.objects.filter(
                consumable_filter | no_facility_filter
            )
            if self.instance.pk:
                self.fields["core_facility_consumables"].initial = Consumable.objects.filter(consumable_filter)


@register(CoreFacility)
class CoreFacilityAdmin(admin.ModelAdmin):
    list_display = ["name", "get_external_id"]
    form = CoreFacilityAdminForm

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if "core_facility_tools" in form.changed_data:
            original_items = Tool.objects.filter(core_rel__in=obj.corerelationship_set.filter(tool__isnull=False))
            save_all_core_facility_relationships(
                form.cleaned_data["core_facility_tools"], original_items, obj, "tool", change
            )
        if "core_facility_areas" in form.changed_data:
            original_items = Area.objects.filter(core_rel__in=obj.corerelationship_set.filter(area__isnull=False))
            save_all_core_facility_relationships(
                form.cleaned_data["core_facility_areas"], original_items, obj, "area", change
            )
        if "core_facility_consumables" in form.changed_data:
            original_items = Consumable.objects.filter(
                core_rel__in=obj.corerelationship_set.filter(consumable__isnull=False)
            )
            save_all_core_facility_relationships(
                form.cleaned_data["core_facility_consumables"], original_items, obj, "consumable", change
            )

    @admin.display(ordering="external_id")
    def get_external_id(self, core_facility: CoreFacility):
        return core_facility.external_id


class NewToolAdminForm(ToolAdminForm):
    core_facility = forms.ModelChoiceField(
        queryset=CoreFacility.objects.all(),
        required=False,
        help_text="The core facility this tool belongs to. Used for billing purposes.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and "core_facility" in self.fields:
            self.fields["core_facility"].initial = self.instance.core_facility

    def clean_core_facility(self):
        parent_tool = self.cleaned_data.get("parent_tool")
        core_facility = self.cleaned_data.get("core_facility")
        if not parent_tool and not core_facility and settings.TOOL_CORE_FACILITY_REQUIRED:
            raise ValidationError("This field is required.")
        return core_facility


class NewToolAdmin(ToolAdmin):
    form = NewToolAdminForm

    def save_model(self, request, obj: Tool, form, change):
        super().save_model(request, obj, form, change)
        save_or_delete_core_facility(obj, form.cleaned_data.get("core_facility"), "tool")

    def get_fieldsets(self, request, obj: Area = None):
        # Add core_facility field
        fieldsets = deepcopy(super().get_fieldsets(request, obj))
        fieldsets[0][1]["fields"] = fieldsets[0][1]["fields"] + ("core_facility",)
        return fieldsets


class NewAreaAdminForm(AreaAdminForm):
    core_facility = forms.ModelChoiceField(
        queryset=CoreFacility.objects.all(),
        required=settings.AREA_CORE_FACILITY_REQUIRED,
        help_text="The core facility this area belongs to. Used for billing purposes.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and "core_facility" in self.fields:
            self.fields["core_facility"].initial = self.instance.core_facility


class NewAreaAdmin(AreaAdmin):
    form = NewAreaAdminForm

    def get_fieldsets(self, request, obj: Area = None):
        # Add core_facility field
        fieldsets = deepcopy(super().get_fieldsets(request, obj))
        fieldsets[0][1]["fields"] = fieldsets[0][1]["fields"] + ("core_facility",)
        return fieldsets

    def save_model(self, request, obj: Area, form, change):
        super().save_model(request, obj, form, change)
        save_or_delete_core_facility(obj, form.cleaned_data["core_facility"], "area")


class NewConsumableAdminForm(forms.ModelForm):
    core_facility = forms.ModelChoiceField(
        queryset=CoreFacility.objects.all(),
        required=settings.CONSUMABLE_CORE_FACILITY_REQUIRED,
        help_text="The core facility this consumable belongs to. Used for billing purposes.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and "core_facility" in self.fields:
            self.fields["core_facility"].initial = self.instance.core_facility


class NewConsumableAdmin(ConsumableAdmin):
    form = NewConsumableAdminForm

    def save_model(self, request, obj: Consumable, form, change):
        super().save_model(request, obj, form, change)
        save_or_delete_core_facility(obj, form.cleaned_data["core_facility"], "consumable")


class NewStaffChargeAdminForm(forms.ModelForm):
    core_facility = forms.ModelChoiceField(
        queryset=CoreFacility.objects.all(),
        required=settings.STAFF_CHARGE_CORE_FACILITY_REQUIRED,
        help_text="The core facility this staff charge belongs to. Used for billing purposes.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and "core_facility" in self.fields:
            self.fields["core_facility"].initial = self.instance.core_facility


class NewStaffChargeAdmin(StaffChargeAdmin):
    form = NewStaffChargeAdminForm

    def save_model(self, request, obj: Consumable, form, change):
        super().save_model(request, obj, form, change)
        save_or_delete_core_facility(obj, form.cleaned_data["core_facility"], "staff_charge")


class CustomChargeAdminForm(forms.ModelForm):
    class Meta:
        model = CustomCharge
        fields = "__all__"

    core_facility = forms.ModelChoiceField(
        queryset=CoreFacility.objects.all(),
        required=settings.CUSTOM_CHARGE_CORE_FACILITY_REQUIRED,
        help_text="The core facility this tool belongs to. Used for billing purposes.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not cap_discount_installed():
            hide_form_field(self, "cap_eligible")


@register(CustomCharge)
class CustomChargeAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "amount", "customer", "project", "creator", "core_facility", "waived")
    search_fields = ("name", "customer__first_name", "customer__last_name", "customer__username", "project__name")
    list_filter = ("date", "project", "core_facility", "waived")
    form = CustomChargeAdminForm


class ProjectBillingHardCapAdminForm(forms.ModelForm):
    charge_types = IntMultipleChoiceField(
        choices=BillableItemType.choices(),
        required=True,
        widget=widgets.FilteredSelectMultiple(verbose_name="Types", is_stacked=False),
    )

    class Meta:
        model = ProjectBillingHardCap
        fields = "__all__"


@admin.register(ProjectBillingHardCap)
class ProjectBillingHardCapAdmin(admin.ModelAdmin):
    list_display = ["project", "enabled", "start_date", "end_date", "amount", "get_charge_types"]
    list_filter = ["enabled", "project"]
    form = ProjectBillingHardCapAdminForm

    @admin.display(description="Charge types")
    def get_charge_types(self, instance: ProjectBillingHardCap):
        return instance.get_charge_types_display()


# Re-register ToolAdmin, AreaAdmin & ConsumableAdmin
admin.site.unregister(Tool)
admin.site.register(Tool, NewToolAdmin)
admin.site.unregister(Area)
admin.site.register(Area, NewAreaAdmin)
admin.site.unregister(Consumable)
admin.site.register(Consumable, NewConsumableAdmin)
admin.site.unregister(StaffCharge)
admin.site.register(StaffCharge, NewStaffChargeAdmin)
admin.site.register(InstitutionType)
admin.site.register(Department)
