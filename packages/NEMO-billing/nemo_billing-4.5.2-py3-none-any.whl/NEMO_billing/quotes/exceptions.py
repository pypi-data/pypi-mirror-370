from typing import List

from NEMO_billing.exceptions import BillingException
from NEMO_billing.quotes.models import Quote


class QuoteGenerationException(BillingException):
    def __init__(self, quote: Quote, renderer, e: Exception):
        self.quote = quote
        self.renderer = renderer
        msg = f"Error rendering quote {quote.name} ({quote.id}) with {renderer.__class__.__name__}: {str(e)}."
        super().__init__(msg)


class FailedToSendQuoteEmailException(BillingException):
    def __init__(self, quote: Quote):
        self.quote = quote
        msg = f"Error sending quote {quote.name} ({quote.id}) email."
        super().__init__(msg)
