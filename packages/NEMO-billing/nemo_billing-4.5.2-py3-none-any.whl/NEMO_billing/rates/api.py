from NEMO.serializers import ModelSerializer
from NEMO.utilities import export_format_datetime
from NEMO.views.api import ModelViewSet, boolean_filters, date_filters, key_filters, number_filters
from drf_excel.mixins import XLSXFileMixin
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import mixins
from rest_framework.fields import CharField
from rest_framework.viewsets import ReadOnlyModelViewSet

from NEMO_billing.rates.models import Rate, RateCategory, RateType


class RateCategorySerializer(ModelSerializer):
    class Meta:
        model = RateCategory
        fields = "__all__"


class RateTypeSerializer(ModelSerializer):
    class Meta:
        model = RateType
        fields = "__all__"


class RateSerializer(FlexFieldsModelSerializer, ModelSerializer):
    class Meta:
        model = Rate
        fields = "__all__"
        expandable_fields = {
            "type": "NEMO_billing.rates.api.RateTypeSerializer",
            "tool": "NEMO.serializers.ToolSerializer",
            "area": "NEMO.serializers.AreaSerializer",
            "consumable": "NEMO.serializers.ConsumableSerializer",
        }

    type_name = CharField(source="type.get_type_display", read_only=True)
    category_name = CharField(source="category.name", default=None, read_only=True)
    tool_name = CharField(source="tool.name", default=None, read_only=True)
    area_name = CharField(source="area.name", default=None, read_only=True)
    consumable_name = CharField(source="consumable.name", default=None, read_only=True)


class RateCategoryViewSet(ModelViewSet):
    filename = "rate_categories"
    queryset = RateCategory.objects.all()
    serializer_class = RateCategorySerializer


class RateTypeViewSet(XLSXFileMixin, mixins.UpdateModelMixin, ReadOnlyModelViewSet):
    queryset = RateType.objects.all()
    serializer_class = RateTypeSerializer

    def get_filename(self, *args, **kwargs):
        return f"rate_types-{export_format_datetime()}.xlsx"


class RateViewSet(ModelViewSet):
    filename = "rates"
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    filterset_fields = {
        "type": key_filters,
        "category": key_filters,
        "id": key_filters,
        "tool": key_filters,
        "area": key_filters,
        "consumable": key_filters,
        "amount": number_filters,
        "minimum_charge": number_filters,
        "effective_date": date_filters,
        "flat": boolean_filters,
        "daily": boolean_filters,
        "daily_split_multi_day_charges": boolean_filters,
        "deleted": boolean_filters,
    }
