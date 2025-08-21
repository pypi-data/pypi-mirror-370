from NEMO.serializers import ModelSerializer
from NEMO.views.api import ModelViewSet, boolean_filters, datetime_filters, key_filters, number_filters, string_filters
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.fields import CharField

from NEMO_billing.models import CoreFacility, CustomCharge, Department, Institution, InstitutionType


class CoreFacilitySerializer(ModelSerializer):
    class Meta:
        model = CoreFacility
        fields = "__all__"


class CoreFacilityViewSet(ModelViewSet):
    filename = "core_facilities"
    queryset = CoreFacility.objects.all()
    serializer_class = CoreFacilitySerializer
    filterset_fields = {
        "name": string_filters,
        "external_id": string_filters,
    }


class CustomChargeSerializer(FlexFieldsModelSerializer, ModelSerializer):
    class Meta:
        model = CustomCharge
        fields = "__all__"
        expandable_fields = {
            "customer": "NEMO.serializers.UserSerializer",
            "creator": "NEMO.serializers.UserSerializer",
            "project": "NEMO.serializers.ProjectSerializer",
            "validated_by": "NEMO.serializers.UserSerializer",
            "waived_by": "NEMO.serializers.UserSerializer",
        }

    customer_name = CharField(source="customer.get_name", read_only=True)
    creator_name = CharField(source="creator.get_name", read_only=True)


class CustomChargeViewSet(ModelViewSet):
    filename = "custom_charges"
    queryset = CustomCharge.objects.all()
    serializer_class = CustomChargeSerializer
    filterset_fields = {
        "name": string_filters,
        "customer": key_filters,
        "creator": key_filters,
        "project": key_filters,
        "date": datetime_filters,
        "amount": number_filters,
        "core_facility": key_filters,
        "validated": boolean_filters,
        "validated_by": key_filters,
        "waived": boolean_filters,
        "waived_on": datetime_filters,
        "waived_by": key_filters,
    }


class DepartmentSerializer(ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class DepartmentViewSet(ModelViewSet):
    filename = "departments"
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filterset_fields = {
        "name": string_filters,
    }


class InstitutionTypeSerializer(ModelSerializer):
    class Meta:
        model = InstitutionType
        fields = "__all__"


class InstitutionTypeViewSet(ModelViewSet):
    filename = "institution_types"
    queryset = InstitutionType.objects.all()
    serializer_class = InstitutionTypeSerializer
    filterset_fields = {
        "name": string_filters,
    }


class InstitutionSerializer(FlexFieldsModelSerializer, ModelSerializer):
    class Meta:
        model = Institution
        fields = "__all__"
        expandable_fields = {
            "institution_type": "NEMO_billing.api.InstitutionTypeSerializer",
        }


class InstitutionViewSet(ModelViewSet):
    filename = "institutions"
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    filterset_fields = {
        "name": string_filters,
        "institution_type_id": key_filters,
        "state": string_filters,
        "country": string_filters,
        "zip_code": string_filters,
    }
