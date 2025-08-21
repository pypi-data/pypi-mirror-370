from django.apps import AppConfig
from django.conf import settings

from . import app_settings as defaults

# Set some app default settings
for name in dir(defaults):
    if name.isupper() and not hasattr(settings, name):
        setattr(settings, name, getattr(defaults, name))


class NEMOBillingConfig(AppConfig):
    name = "NEMO_billing"
    verbose_name = "Billing"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from NEMO.plugins.utils import check_extra_dependencies
        from NEMO_billing.admin import CoreFacilityAdmin
        from NEMO_billing.customization import BillingCustomization

        check_extra_dependencies(self.name, ["NEMO", "NEMO-CE"])
        # update the short_description for core facility's external identifier here after initialization
        CoreFacilityAdmin.get_external_id.short_description = BillingCustomization.get(
            "billing_core_facility_external_id_name", raise_exception=False
        )
