import ntpath
import os
from datetime import datetime
from decimal import Decimal
from typing import Iterable, List, Optional

from NEMO.utilities import EmptyHttpRequest, render_email_template, send_mail
from NEMO.views.customization import get_media_file_contents
from django.conf import settings
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.utils.formats import number_format
from django.utils.text import slugify

from NEMO_billing.invoices.customization import InvoiceCustomization


def export_invoice_filename(invoice):
    invoice_filename_template = InvoiceCustomization.get("invoice_zip_export_template")
    default_template = InvoiceCustomization.variables["invoice_zip_export_template"]
    dictionary = {
        "invoice": invoice,
        "project_name": slugify(invoice.project_details.name),
        "account_name": slugify(invoice.project_details.project.account.name),
    }
    try:
        filename = Template(invoice_filename_template).render(Context(dictionary))
    except:
        filename = Template(default_template).render(Context(dictionary))
    return filename


def get_invoice_document_filename(invoice, filename):
    account_name = slugify(invoice.project_details.project.account.name)
    project_name = slugify(invoice.project_details.name)
    now = datetime.now()
    # generated_date = now.strftime("%Y-%m-%d_%H-%M-%S")
    year = now.strftime("%Y")
    ext = os.path.splitext(filename)[1]
    return f"invoices/{year}/{account_name}/{project_name}/{slugify(invoice.invoice_number)}_{project_name}{ext}"


def get_merchant_logo_filename(configuration, filename):
    name = slugify(configuration.name + "_merchant_logo")
    ext = os.path.splitext(filename)[1]
    return f"merchant_logos/{name}{ext}"


def display_amount(amount: Optional[Decimal], configuration=None) -> str:
    # We need to specifically check for None since amount = 0 will evaluate to False
    if amount is None:
        return ""
    rounded_amount = round(amount, 2)
    currency = (
        f"{configuration.currency_symbol}"
        if configuration and configuration.currency_symbol
        else f"{configuration.currency} " if configuration and configuration.currency else ""
    )
    if amount < 0:
        return f"({currency}{number_format(abs(rounded_amount), decimal_pos=2)})"
    else:
        return f"{currency}{number_format(rounded_amount, decimal_pos=2)}"


def render_and_send_email(template_prefix, context, from_email, to=None, bcc=None, cc=None, attachments=None) -> int:
    subject = render_template_from_media("{0}_subject.txt".format(template_prefix), context)
    # remove superfluous line breaks
    subject = " ".join(subject.splitlines()).strip()
    subject = format_email_subject(subject)
    template_name = "{0}_message.html".format(template_prefix)
    content = render_template_from_media(template_name, context).strip()
    return send_mail(
        subject=subject, content=content, from_email=from_email, to=to, bcc=bcc, cc=cc, attachments=attachments
    )


def format_email_subject(subject):
    prefix = getattr(settings, "INVOICE_EMAIL_SUBJECT_PREFIX", "")
    return prefix + force_str(subject)


def render_template_from_media(template_name, context):
    """Try to find the template in media folder. if it doesn't exist, look in project templates"""
    file_name = os.path.basename(template_name)
    email_contents = get_media_file_contents(file_name)
    if email_contents:
        return render_email_template(email_contents, context)
    else:
        # otherwise, look in templates
        return render_to_string(template_name, context, EmptyHttpRequest())


def category_name_for_item_type(billable_item_type) -> str:
    from NEMO_billing.invoices.processors import invoice_data_processor_class

    return invoice_data_processor_class.category_name_for_item_type(billable_item_type)


def name_for_billable_item(billable_item) -> str:
    from NEMO_billing.invoices.processors import invoice_data_processor_class

    return invoice_data_processor_class.name_for_item(billable_item)


def flatten(iterable: Iterable[Iterable]) -> List:
    return [item for sublist in iterable for item in sublist]
