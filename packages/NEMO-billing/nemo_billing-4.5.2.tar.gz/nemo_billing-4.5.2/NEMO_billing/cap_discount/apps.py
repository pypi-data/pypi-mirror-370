from django.apps import AppConfig
from django.conf import settings

from . import app_settings as defaults

# Set some app default settings
for name in dir(defaults):
    if name.isupper() and not hasattr(settings, name):
        setattr(settings, name, getattr(defaults, name))


class CapConfig(AppConfig):
    name = "NEMO_billing.cap_discount"
    verbose_name = "Billing Cap Discount"
    default_auto_field = "django.db.models.AutoField"
