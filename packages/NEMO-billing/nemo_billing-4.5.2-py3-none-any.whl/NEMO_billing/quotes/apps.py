from django.apps import AppConfig
from django.conf import settings

from . import app_settings as defaults

for name in dir(defaults):
    if name.isupper() and not hasattr(settings, name):
        setattr(settings, name, getattr(defaults, name))


class NEMOQuotesConfig(AppConfig):
    name = "NEMO_billing.quotes"
    verbose_name = "Billing Quotes"
    default_auto_field = "django.db.models.AutoField"
    plugin_id = 12100  # Used to make EmailCategory and other IntegerChoices ranges unique

    def ready(self):
        from NEMO_billing.quotes.customization import QuoteCustomization
        from django.utils.translation import gettext_lazy as _
        from NEMO.plugins.utils import add_dynamic_notification_types, add_dynamic_email_categories
        from NEMO_billing.quotes.utilities import QUOTE_REVIEW_NOTIFICATION, QUOTE_EMAIL_CATEGORY

        add_dynamic_notification_types([(QUOTE_REVIEW_NOTIFICATION, _("Quote action - notifies quote reviewers"))])
        add_dynamic_email_categories([(QUOTE_EMAIL_CATEGORY, _("Billing quotes"))])
