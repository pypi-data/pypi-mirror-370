from NEMO.decorators import customization
from NEMO.views.customization import CustomizationBase
from django.core.validators import validate_comma_separated_integer_list, validate_email


@customization(key="billing", title="Billing")
class BillingCustomization(CustomizationBase):
    variables = {
        "billing_accounting_email_address": "",
        "billing_project_expiration_reminder_days": "",
        "billing_project_expiration_reminder_cc": "",
        "billing_usage_show_pending_vs_final": "",
        "billing_core_facility_external_id_name": "External ID",
    }
    files = [
        ("billing_project_expiration_reminder_email_subject", ".txt"),
        ("billing_project_expiration_reminder_email_message", ".html"),
    ]

    def validate(self, name, value):
        if name == "billing_project_expiration_reminder_days" and value:
            # Check that we have an integer or a list of integers
            validate_comma_separated_integer_list(value)
        elif name == "billing_accounting_email_address" and value:
            validate_email(value)
        elif name == "billing_project_expiration_reminder_cc":
            recipients = tuple([e for e in value.split(",") if e])
            for email in recipients:
                validate_email(email)

    @classmethod
    def set(cls, name, value):
        super().set(name, value)
        from NEMO_billing.admin import CoreFacilityAdmin

        if name and name == "billing_core_facility_external_id_name":
            CoreFacilityAdmin.get_external_id.short_description = value
