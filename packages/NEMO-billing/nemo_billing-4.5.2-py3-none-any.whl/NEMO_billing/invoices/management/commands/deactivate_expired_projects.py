from django.core.management import BaseCommand

from NEMO_billing.invoices.views.project import do_deactivate_expired_projects


class Command(BaseCommand):
    help = "Run every day to deactivate expired projects."

    def handle(self, *args, **options):
        do_deactivate_expired_projects()
