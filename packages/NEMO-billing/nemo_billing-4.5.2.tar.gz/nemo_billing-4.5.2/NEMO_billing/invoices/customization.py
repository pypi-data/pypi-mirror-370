from datetime import datetime
from typing import Dict

from NEMO.decorators import customization
from NEMO.utilities import get_month_timeframe
from NEMO.views.customization import CustomizationBase
from django.core.exceptions import ValidationError
from django.template import Context, Template


@customization(key="invoices", title="Billing invoices")
class InvoiceCustomization(CustomizationBase):
    variables = {
        "invoice_number_format": "{:05d}",
        "invoice_number_current": "0",
        "invoice_zip_export_template": "{{ account_name }}/{{ project_name }}-{{ invoice.start|date:'Y' }}-{{ invoice.start|date:'F' }}-{{ invoice.invoice_number|slugify }}",
        "invoice_month_list_since": "",
        "invoice_funds_show_total_balance": "",
        "invoice_show_hard_cap_status": "",
        "invoice_skip_inactive_projects": "",
        "invoice_skip_inactive_accounts": "",
    }
    files = [
        ("email_send_invoice_subject", ".txt"),
        ("email_send_invoice_message", ".html"),
        ("email_send_invoice_reminder_subject", ".txt"),
        ("email_send_invoice_reminder_message", ".html"),
    ]

    def context(self) -> Dict:
        # Adding invoice number formatted to the template
        customization_context = super().context()
        try:
            customization_context["invoice_number_formatted"] = self.get("invoice_number_format").format(
                int(self.get("invoice_number_current"))
            )
        except:
            pass
        try:
            customization_context["invoice_zip_template_formatted"] = (
                self.invoice_template_validation_context(self.get("invoice_zip_export_template")) + ".pdf"
            )
        except:
            pass
        return customization_context

    def validate(self, name, value):
        if name == "invoice_number_format":
            try:
                value.format(123)
            except Exception as e:
                raise ValidationError(str(e))
        elif name == "invoice_zip_export_template":
            try:
                self.invoice_template_validation_context(value)
            except Exception as e:
                raise ValidationError(str(e))
        elif name == "invoice_month_list_since" and value:
            self.validate_date(value)

    def invoice_template_validation_context(self, value):
        from NEMO_billing.invoices.models import Invoice

        invoice = Invoice()
        invoice.invoice_number = invoice.generate_invoice_number()
        month = datetime.now().month - 1
        if month == 0:
            month = 12
        invoice_date = datetime.now().replace(month=month)
        invoice.start, invoice.end = get_month_timeframe(invoice_date.isoformat())
        invoice.created_date = datetime.now()
        return Template(value).render(
            Context({"invoice": invoice, "project_name": "test-project", "account_name": "test-account"})
        )
