from django.urls import path

from NEMO_billing.cap_discount import views

urlpatterns = [
    path("usage_cap_discounts/", views.usage_cap_discounts, name="usage_cap_discounts"),
    path("usage_cap_discounts_user/<int:user_id>/", views.usage_cap_discounts_user, name="usage_cap_discounts_user"),
    path(
        "usage_cap_discounts_account/<int:account_id>/",
        views.usage_cap_discounts_account,
        name="usage_cap_discounts_account",
    ),
    path("cap_discount_status/", views.cap_discount_status, name="cap_discount_status"),
    path(
        "cap_discount_status/configuration/<int:configuration_id>/",
        views.cap_discount_status,
        name="cap_discount_status_configuration",
    ),
]
