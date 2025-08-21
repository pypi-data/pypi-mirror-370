from NEMO.models import Account
from NEMO.utilities import format_datetime

from NEMO_billing.cap_discount.models import CAPDiscountAmount
from NEMO_billing.exceptions import BillingException


class MissingCAPAmountException(BillingException):
    def __init__(self, month, account: Account):
        msg = f"Could not find prior CAP records for {month.strftime('%B %Y')} for account: '{account.name}'. Please generate invoices for that month and try again."
        super().__init__(msg)


class NotLatestInvoiceException(BillingException):
    def __init__(self, amount: CAPDiscountAmount):
        msg = "You can only void/delete the latest invoices when a CAP is associated with it."
        if amount:
            msg += (
                f" The latest amount for the {amount.cap_discount} is on {format_datetime(amount.amount_date, 'F Y')}"
            )
        super().__init__(msg)
