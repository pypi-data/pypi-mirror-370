from typing import Iterable

from NEMO.templatetags.custom_tags_and_filters import app_installed
from django import template

from NEMO_billing.invoices.utilities import display_amount as amount

register = template.Library()


@register.filter
def display_amount(value, configuration=None):
    if value is not None and configuration:
        return amount(value, configuration)


@register.filter
def to_dict(value: Iterable, attribute=None):
    return {getattr(item, attribute, None): item for item in value}


@register.simple_tag()
def cap_discount_installed():
    # CAP discount needs to be installed and the data processor has to be set to CAPDiscountInvoiceDataProcessor
    if app_installed("NEMO_billing.cap_discount"):
        from NEMO_billing.invoices.processors import invoice_data_processor_class as data_processor
        from NEMO_billing.cap_discount.processors import CAPDiscountInvoiceDataProcessor

        return isinstance(data_processor, CAPDiscountInvoiceDataProcessor)
    return False
