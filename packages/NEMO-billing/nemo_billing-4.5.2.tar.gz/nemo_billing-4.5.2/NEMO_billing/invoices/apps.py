from django.apps import AppConfig
from django.conf import settings

from . import app_settings as defaults

# Set some app default settings
for name in dir(defaults):
    if name.isupper() and not hasattr(settings, name):
        setattr(settings, name, getattr(defaults, name))


class NEMOInvoicesConfig(AppConfig):
    name = "NEMO_billing.invoices"
    verbose_name = "Billing Invoices"
    default_auto_field = "django.db.models.AutoField"
