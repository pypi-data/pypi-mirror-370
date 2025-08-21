from NEMO.urls import router, sort_urls
from django.urls import path, re_path

from NEMO_billing.invoices import api
from NEMO_billing.invoices.views import invoices, project, usage


def replace_api_url(url_to_replace, new_config):
    for reg in router.registry:
        if reg[0] == url_to_replace:
            router.registry.remove(reg)
    router.register(*new_config)


# Rest API URLs
router.register(r"billing/projects", api.ProjectWithDetailsViewSet, basename="projects_with_details")
router.register(r"billing/invoice_payments", api.InvoicePaymentViewSet)
router.register(r"billing/billing_data", api.BillingDataViewSet, basename="billingdata")
replace_api_url("projects", (r"projects", api.ProjectWithDetailsViewSet))
router.registry.sort(key=sort_urls)

urlpatterns = [
    path("invoices/", invoices.invoices, name="invoices"),
    path("invoices/filter/<int:year>/", invoices.invoices, name="invoices_year"),
    path("invoices/filter/<int:year>/<int:month>/", invoices.invoices, name="invoices_month"),
    path("invoices/search/", invoices.search_invoices, name="search_invoices"),
    path("invoices/<int:invoice_id>/", invoices.view_invoice, name="view_invoice"),
    path("invoices/<int:invoice_id>/review/", invoices.review_invoice, name="review_invoice"),
    path("invoices/<int:invoice_id>/send/", invoices.send_invoice, name="send_invoice"),
    path("invoices/<int:invoice_id>/void/", invoices.void_invoice, name="void_invoice"),
    path("invoices/<int:invoice_id>/delete/", invoices.delete_invoice, name="delete_invoice"),
    path("invoices/<int:invoice_id>/csv/", invoices.csv_invoice, name="csv_invoice"),
    path("invoices/<int:invoice_id>/re_render/", invoices.re_render_invoice, name="re_render_invoice"),
    path(
        "invoices/<int:invoice_id>/mark_paid_in_full/",
        invoices.mark_invoice_paid_in_full,
        name="mark_invoice_as_paid_in_full",
    ),
    path("invoices/zip/", invoices.zip_invoices, name="zip_invoices"),
    re_path(r"invoices/zip/(?P<file_type>csv)/$", invoices.zip_invoices, name="zip_invoices"),
    path("invoices/review_and_send/", invoices.review_and_send_invoices, name="review_and_send_invoices"),
    path("invoices/generate_monthly_invoices/", invoices.generate_monthly_invoices, name="generate_monthly_invoices"),
    path("invoices/mark_paid_in_full/", invoices.mark_invoices_paid_in_full, name="mark_invoices_as_paid_in_full"),
    path(
        "invoice_payment/<int:invoice_id>/received", invoices.invoice_payment_received, name="invoice_payment_received"
    ),
    path(
        "invoice_payment/<int:payment_id>/processed",
        invoices.invoice_payment_processed,
        name="invoice_payment_processed",
    ),
    # Overriding NEMO's create project URLs
    path("create_project/", project.edit_project, name="invoices_create_project"),
    path("projects/<int:project_id>/edit/", project.edit_project, name="invoices_edit_project"),
    # Overriding NEMO's account and project URLs to add billing details
    path(
        "project/<int:identifier>/", project.custom_project_view, kwargs={"kind": "project"}, name="custom_project_view"
    ),
    path(
        "account/<int:identifier>/", project.custom_project_view, kwargs={"kind": "account"}, name="custom_account_view"
    ),
    # Overriding NEMO's usage URLs to add rate and cost
    path("project_usage/", usage.project_usage, name="project_usage"),
    path("usage/user/", usage.user_usage, name="usage_user"),
    path("usage/staff/", usage.staff_usage, name="usage_staff"),
    # Billing related periodic events
    path(
        "invoices/send_invoice_payment_reminder/",
        invoices.send_invoice_payment_reminder,
        name="send_invoice_payment_reminder",
    ),
    path(
        "projects/deactivate_expired_projects/", project.deactivate_expired_projects, name="deactivate_expired_projects"
    ),
]
