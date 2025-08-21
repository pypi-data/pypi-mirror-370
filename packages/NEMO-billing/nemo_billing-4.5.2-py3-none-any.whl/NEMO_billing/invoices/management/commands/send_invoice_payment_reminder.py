from django.core.management import BaseCommand

from NEMO_billing.invoices.views.invoices import do_send_invoice_payment_reminder


class Command(BaseCommand):
    help = "Run every day to send payment reminders for unpaid invoices."

    def handle(self, *args, **options):
        do_send_invoice_payment_reminder()
