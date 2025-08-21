from NEMO.urls import router, sort_urls
from django.conf import settings
from django.urls import path

from NEMO_billing.rates import api, views

# Rest API URLs
router.register(r"billing/rates", api.RateViewSet)
router.register(r"billing/rate_types", api.RateTypeViewSet)
router.register(r"billing/rate_categories", api.RateCategoryViewSet)
router.registry.sort(key=sort_urls)

urlpatterns = [
    path("rates/", views.rates, name="rates"),
    path("rates/<str:rate_type_choice>/", views.rates, name="rates"),
    path("rate/", views.create_or_modify_rate, name="create_rate"),
    path("rate/<str:rate_type_choice>/", views.create_or_modify_rate, name="create_rate"),
    path("rate/<str:rate_type_choice>/<int:item_id>/", views.create_or_modify_rate, name="create_rate"),
    path("rate_time/<int:rate_id>/", views.delete_rate_time, name="delete_rate_time"),
    path(f"{settings.RATE_LIST_URL}/", views.rate_list, name="rate_list"),
    path(f"{settings.RATE_LIST_URL}/<str:rate_type_choice>/", views.rate_list, name="rate_list"),
]
