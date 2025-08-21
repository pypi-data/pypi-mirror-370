from NEMO.serializers import ModelSerializer
from NEMO.views.api import ModelViewSet, key_filters
from rest_flex_fields import FlexFieldsModelSerializer

from NEMO_billing.prepayments.models import Fund, FundType, ProjectPrepaymentDetail


class ProjectPrepaymentDetailSerializer(FlexFieldsModelSerializer, ModelSerializer):
    class Meta:
        model = ProjectPrepaymentDetail
        fields = "__all__"
        expandable_fields = {
            "project": "NEMO.serializers.ProjectSerializer",
        }


class FundTypeSerializer(ModelSerializer):
    class Meta:
        model = FundType
        fields = "__all__"


class FundSerializer(FlexFieldsModelSerializer, ModelSerializer):
    class Meta:
        model = Fund
        fields = "__all__"
        expandable_fields = {
            "fund_type": "NEMO_billing.prepayments.api.FundTypeSerializer",
            "project_prepayment": "NEMO_billing.prepayments.api.ProjectPrepaymentDetailSerializer",
        }


class FundTypeViewSet(ModelViewSet):
    filename = "fund_types"
    queryset = FundType.objects.all()
    serializer_class = FundTypeSerializer


class FundViewSet(ModelViewSet):
    filename = "funds"
    queryset = Fund.objects.all()
    serializer_class = FundSerializer
    filterset_fields = {
        "id": key_filters,
        "fund_type": key_filters,
        "project_prepayment": key_filters,
    }


class ProjectPrepaymentDetailViewSet(ModelViewSet):
    filename = "project_prepayments"
    queryset = ProjectPrepaymentDetail.objects.all()
    serializer_class = ProjectPrepaymentDetailSerializer
    filterset_fields = {
        "id": key_filters,
        "project": key_filters,
    }
