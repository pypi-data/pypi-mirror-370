from NEMO.urls import router, sort_urls
from django.urls import path, re_path

from NEMO_billing import api, views

# Rest API URLs
router.register(r"billing/core_facilities", api.CoreFacilityViewSet)
router.register(r"billing/custom_charges", api.CustomChargeViewSet)
router.register(r"billing/departments", api.DepartmentViewSet)
router.register(r"billing/institution_types", api.InstitutionTypeViewSet)
router.register(r"billing/institutions", api.InstitutionViewSet)
router.registry.sort(key=sort_urls)

urlpatterns = [
    path("custom_charges/", views.custom_charges, name="custom_charges"),
    path("custom_charge/", views.create_or_modify_custom_charge, name="create_custom_charge"),
    path("custom_charge/<int:custom_charge_id>", views.create_or_modify_custom_charge, name="edit_custom_charge"),
    path(
        "get_projects_for_custom_charges/",
        views.get_projects_for_custom_charges,
        name="get_projects_for_custom_charges",
    ),
    # Overriding NEMO create staff charge URLs to add core facility selection
    path("staff_charges/", views.custom_staff_charges, name="staff_charges"),
    path("begin_staff_charge/", views.custom_begin_staff_charge, name="begin_staff_charge"),
    # Overriding NEMO enable tool URL to set the core facility on staff charge based on the tool's core facility
    path(
        "enable_tool/<int:tool_id>/user/<int:user_id>/project/<int:project_id>/staff_charge/<str:staff_charge>/",
        views.custom_enable_tool,
        name="enable_tool",
    ),
    # Override broadcast email to add new search for PIs by institution types
    path("email_broadcast/", views.email_broadcast, name="email_broadcast"),
    re_path(
        r"^email_broadcast/(?P<audience>tool|area|account|project|project-pis|user|tool-reservation|group|pi_institution_types)/$",
        views.email_broadcast,
        name="email_broadcast",
    ),
]
