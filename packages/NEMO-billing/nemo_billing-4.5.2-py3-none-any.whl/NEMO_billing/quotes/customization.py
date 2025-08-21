from NEMO.decorators import customization
from NEMO.views.customization import CustomizationBase


@customization(key="quotes", title="Billing quotes")
class QuoteCustomization(CustomizationBase):
    variables = {}
    files = [
        ("quote_approval_request_email", ".html"),
        ("quote_status_update_email", ".html"),
        ("quote_email", ".html"),
    ]
