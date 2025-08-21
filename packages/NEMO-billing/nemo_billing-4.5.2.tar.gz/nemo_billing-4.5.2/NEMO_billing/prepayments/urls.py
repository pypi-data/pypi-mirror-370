from NEMO.urls import router, sort_urls
from django.urls import path

from NEMO_billing.prepayments import api
from NEMO_billing.prepayments.views import prepayments

# Rest API URLs
router.register(r"billing/funds", api.FundViewSet)
router.register(r"billing/fund_types", api.FundTypeViewSet)
router.register(r"billing/project_prepayments", api.ProjectPrepaymentDetailViewSet)
router.registry.sort(key=sort_urls)

urlpatterns = [
    path("usage_project_prepayments/", prepayments.usage_project_prepayments, name="usage_project_prepayments"),
    path("prepaid_project_status/", prepayments.prepaid_project_status, name="prepaid_project_status"),
]
