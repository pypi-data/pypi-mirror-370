from NEMO.utilities import format_datetime
from django import forms
from django.contrib import admin
from django.contrib.admin import widgets

from NEMO_billing.invoices.models import BillableItemType
from NEMO_billing.prepayments.models import Fund, FundType, ProjectPrepaymentDetail
from NEMO_billing.utilities import IntMultipleChoiceField


class ProjectPrepaymentDetailAdminForm(forms.ModelForm):
    charge_types = IntMultipleChoiceField(
        choices=BillableItemType.choices_except(BillableItemType.CUSTOM_CHARGE, BillableItemType.CONSUMABLE),
        required=True,
        widget=widgets.FilteredSelectMultiple(verbose_name="Types", is_stacked=False),
    )

    class Meta:
        model = ProjectPrepaymentDetail
        fields = "__all__"


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "get_project",
        "get_account",
        "fund_type",
        "amount",
        "balance",
        "get_balance_date_display",
        "get_start_display",
        "get_expiration_display",
        "reference",
        "balance_warning_percent",
    ]
    list_filter = [
        ("fund_type", admin.RelatedOnlyFieldListFilter),
        ("project_prepayment__project", admin.RelatedOnlyFieldListFilter),
        ("project_prepayment__project__account", admin.RelatedOnlyFieldListFilter),
    ]

    @admin.display(description="Project", ordering="project_prepayment__project")
    def get_project(self, obj: Fund):
        return obj.project_prepayment.project

    @admin.display(description="Account", ordering="project_prepayment__project__account")
    def get_account(self, obj: Fund):
        return obj.project_prepayment.project.account

    @admin.display(description="Start", ordering=["start_year", "start_month"])
    def get_start_display(self, obj: Fund):
        return format_datetime(obj.start_date, "F Y")

    @admin.display(description="Expires", ordering=["expiration_year", "expiration_month"])
    def get_expiration_display(self, obj: Fund):
        if obj.expiration_date:
            return format_datetime(obj.expiration_date, "F Y")

    @admin.display(description="Balance date", ordering="balance_date")
    def get_balance_date_display(self, obj: Fund):
        return format_datetime(obj.project_prepayment.balance_last_updated, "SHORT_DATE_FORMAT")


@admin.register(ProjectPrepaymentDetail)
class ProjectPrepaymentDetailAdmin(admin.ModelAdmin):
    list_display = ["project", "get_charge_types", "get_only_core_facilities", "overdraft_amount_allowed"]
    filter_horizontal = ["only_core_facilities"]
    form = ProjectPrepaymentDetailAdminForm

    @admin.display(description="Core facilities allowed")
    def get_only_core_facilities(self, instance: ProjectPrepaymentDetail):
        return instance.get_only_core_facilities_display()

    @admin.display(description="Charge types allowed")
    def get_charge_types(self, instance: ProjectPrepaymentDetail):
        return instance.get_charge_types_display()


admin.site.register(FundType)
