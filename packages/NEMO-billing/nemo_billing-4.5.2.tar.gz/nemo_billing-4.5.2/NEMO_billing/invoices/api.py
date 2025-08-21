from copy import deepcopy

from NEMO.constants import CHAR_FIELD_MEDIUM_LENGTH
from NEMO.models import Project
from NEMO.serializers import ModelSerializer, ProjectSerializer
from NEMO.utilities import export_format_datetime
from NEMO.views.api import ModelViewSet, ProjectViewSet, date_filters, datetime_filters, key_filters
from NEMO.views.api_billing import BillingFilterForm
from django import forms
from django.db.models import Q
from drf_excel.mixins import XLSXFileMixin
from rest_flex_fields.serializers import FlexFieldsSerializerMixin
from rest_framework import status
from rest_framework.fields import BooleanField, CharField, DateTimeField, DecimalField, IntegerField, empty
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from NEMO_billing.customization import BillingCustomization
from NEMO_billing.invoices.customization import InvoiceCustomization
from NEMO_billing.invoices.models import InvoiceConfiguration, InvoicePayment, ProjectBillingDetails
from NEMO_billing.invoices.processors import invoice_data_processor_class as data_processor
from NEMO_billing.invoices.views.usage import augment_with_invoice_items


class NewBillingFilterForm(BillingFilterForm):
    include_no_charge_projects = forms.BooleanField(initial=False, required=False)

    def get_include_no_charge_projects(self):
        return self.cleaned_data["include_no_charge_projects"]


class ProjectBillingDetailsSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    class Meta:
        model = ProjectBillingDetails
        exclude = ("project",)


class ProjectWithDetailsSerializer(ProjectSerializer):
    projectbillingdetails = ProjectBillingDetailsSerializer(required=False)

    class Meta(ProjectSerializer.Meta):
        ProjectSerializer.Meta.expandable_fields.update(
            {
                "category": (
                    "NEMO_billing.rates.api.RateCategorySerializer",
                    {"source": "projectbillingdetails.category"},
                ),
                "institution": (
                    "NEMO_billing.api.InstitutionSerializer",
                    {"source": "projectbillingdetails.institution"},
                ),
                "department": ("NEMO_billing.api.DepartmentSerializer", {"source": "projectbillingdetails.department"}),
            }
        )

    def get_fields(self):
        fields = super().get_fields()
        detail_fields = fields.pop("projectbillingdetails", {})
        if detail_fields:
            for key, value in detail_fields.fields.items():
                if key != "id":
                    # reset the source to details
                    value.source = "projectbillingdetails." + value.source
                    value.source_attrs = value.source.split(".")
                    fields[key] = value
        return fields

    def validate(self, attrs):
        attributes_data = dict(attrs)
        details_attrs = attributes_data.pop("projectbillingdetails", {})
        super().validate(attributes_data)
        project_details = get_billing_details(self.instance)
        for details_attr, details_value in details_attrs.items():
            setattr(project_details, details_attr, details_value)
        ProjectBillingDetailsSerializer().full_clean(project_details, exclude=["project"])
        return attrs

    def update(self, instance, validated_data) -> Project:
        data = deepcopy(validated_data)
        details_data = data.pop("projectbillingdetails", {})
        project_instance = super().update(instance, data)
        project_details = get_billing_details(project_instance)
        ProjectBillingDetailsSerializer().update(project_details, details_data)
        return project_instance

    def create(self, validated_data) -> Project:
        data = deepcopy(validated_data)
        details_data = data.pop("projectbillingdetails", {})
        project_instance = super().create(data)
        details_data["project"] = project_instance
        ProjectBillingDetailsSerializer().create(details_data)
        return project_instance


class ProjectWithDetailsViewSet(ProjectViewSet):
    serializer_class = ProjectWithDetailsSerializer


class InvoicePaymentSerializer(ModelSerializer):
    class Meta:
        model = InvoicePayment
        fields = "__all__"


class InvoicePaymentViewSet(ModelViewSet):
    filename = "invoice_payments"
    queryset = InvoicePayment.objects.all()
    serializer_class = InvoicePaymentSerializer
    filterset_fields = {
        "id": key_filters,
        "payment_received": date_filters,
        "payment_processed": date_filters,
        "created_date": datetime_filters,
        "updated_date": datetime_filters,
        "invoice_id": key_filters,
    }


class BillingDataSerializer(Serializer):
    item_type = CharField(source="item_type.display_name", read_only=True)
    item_id = IntegerField(source="item.id", read_only=True)
    core_facility = CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH, read_only=True)
    name = CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH, read_only=True)
    account = CharField(source="project.account.name", read_only=True)
    account_id = IntegerField(source="project.account.id", read_only=True)
    project = CharField(source="project.name", read_only=True)
    project_id = IntegerField(source="project.id", read_only=True)
    institution = CharField(source="project.projectbillingdetails.institution.name", read_only=True, allow_null=True)
    institution_id = IntegerField(
        source="project.projectbillingdetails.institution.id", read_only=True, allow_null=True
    )
    department = CharField(source="project.projectbillingdetails.department.name", read_only=True, allow_null=True)
    department_id = IntegerField(source="project.projectbillingdetails.department.id", read_only=True, allow_null=True)
    application = CharField(source="project.application_identifier", read_only=True)
    reference_po = CharField(source="project.application_identifier", read_only=True)
    user = CharField(source="user.username", read_only=True)
    user_fullname = CharField(source="user.get_name", read_only=True)
    proxy_user = CharField(source="proxy_user.username", read_only=True, allow_null=True)
    proxy_user_fullname = CharField(source="proxy_user.get_name", read_only=True, allow_null=True)
    start = DateTimeField(read_only=True)
    end = DateTimeField(read_only=True)
    quantity = DecimalField(read_only=True, decimal_places=2, max_digits=8)
    rate = CharField(source="billable_rate", read_only=True)
    rate_category = CharField(source="rate.category", read_only=True, allow_null=True)
    rate_time_name = CharField(source="rate.time.name", read_only=True, allow_null=True)
    rate_time_id = IntegerField(source="rate.time.id", read_only=True, allow_null=True)
    unit_rate = DecimalField(source="rate.amount", read_only=True, decimal_places=2, max_digits=14, allow_null=True)
    unit_type = CharField(read_only=True, allow_null=True)
    unit_quantity = DecimalField(read_only=True, decimal_places=2, max_digits=14, allow_null=True)
    validated = BooleanField(read_only=True)
    validated_by = CharField(source="validated_by.username", read_only=True, allow_null=True)
    waived = BooleanField(read_only=True)
    waived_by = CharField(read_only=True, source="waived_by.username", allow_null=True)
    waived_on = DateTimeField(read_only=True)
    amount = DecimalField(source="invoiced_amount", read_only=True, decimal_places=2, max_digits=14)
    discount_amount = DecimalField(source="invoiced_discount", read_only=True, decimal_places=2, max_digits=14)
    pending_amount = DecimalField(source="amount", read_only=True, decimal_places=2, max_digits=14)
    merged_amount = DecimalField(label="amount", read_only=True, decimal_places=2, max_digits=14)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        pending_vs_final = BillingCustomization.get_bool("billing_usage_show_pending_vs_final")
        if not pending_vs_final:
            self.fields["amount"] = self.fields["merged_amount"]
            del self.fields["pending_amount"]
        del self.fields["merged_amount"]

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        fields = "__all__"


class BillingDataViewSet(XLSXFileMixin, GenericViewSet):
    serializer_class = BillingDataSerializer

    def list(self, request, *args, **kwargs):
        billing_form = NewBillingFilterForm(self.request.GET)
        if not billing_form.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=billing_form.errors)
        try:
            queryset = self.get_queryset()
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def check_permissions(self, request):
        if not request or not request.user.has_perm("NEMO.use_billing_api"):
            self.permission_denied(request)

    def get_queryset(self):
        billing_form = NewBillingFilterForm(self.request.GET)
        billing_form.full_clean()

        queryset = Q()
        if not billing_form.get_include_no_charge_projects():
            queryset &= Q(project__projectbillingdetails__no_charge=False)
        if InvoiceCustomization.get_bool("invoice_skip_inactive_projects"):
            queryset &= Q(project__active=True)
        if InvoiceCustomization.get_bool("invoice_skip_inactive_accounts"):
            queryset &= Q(project__account__active=True)
        start, end = billing_form.get_start_date(), billing_form.get_end_date()
        if billing_form.get_account_id():
            queryset &= Q(project__account_id=billing_form.get_account_id())
        if billing_form.get_account_name():
            queryset &= Q(project__account__name=billing_form.get_account_name())
        if billing_form.get_project_id():
            queryset &= Q(project_id=billing_form.get_project_id())
        if billing_form.get_project_name():
            queryset &= Q(project__name=billing_form.get_project_name())
        if billing_form.get_application_name():
            queryset &= Q(project__application_identifier=billing_form.get_application_name())
        user_filter, customer_filter, trainee_filter = queryset, queryset, queryset
        if billing_form.get_username():
            user_filter = user_filter & Q(user__username=billing_form.get_username())
            customer_filter = customer_filter & Q(customer__username=billing_form.get_username())
            trainee_filter = trainee_filter & Q(trainee__username=billing_form.get_username())

        config = InvoiceConfiguration.first_or_default()
        billables = data_processor.get_billable_items(start, end, config, customer_filter, user_filter, trainee_filter)
        augment_with_invoice_items(billables)
        billables.sort(key=lambda x: x.start, reverse=True)
        return billables

    def get_filename(self, *args, **kwargs):
        return f"billing-{export_format_datetime()}.xlsx"


def get_billing_details(project: Project):
    try:
        project_details = project.projectbillingdetails
    except (ProjectBillingDetails.DoesNotExist, AttributeError):
        project_details = ProjectBillingDetails(project=project)
    return project_details
