from typing import Dict

from NEMO.decorators import customization
from NEMO.exceptions import InvalidCustomizationException
from NEMO.models import Tool
from NEMO.views.customization import CustomizationBase
from django.core.exceptions import ValidationError
from django.core.validators import validate_comma_separated_integer_list

from NEMO_billing.rates.models import RateCategory, RateType


@customization(key="billing_rates", title="Billing rates")
class BillingRatesCustomization(CustomizationBase):
    variables = {
        "rates_hide_table": "",
        "rates_usage_hide_charges": "",
        "rates_hide_consumable_rates": "",
        "rates_expand_table": "",
        "rates_daily_per_account": "",
        "rates_show_all_categories": "",
        "rates_rate_list_page_access": "",
        "rates_rate_list_page_show_types": "",
        "rates_rate_list_page_show_categories": "",
        "rates_rate_list_show_zero_rates": "",
        "rates_rate_list_show_facilities": "",
        "rates_rate_list_excluded_tools": "",
    }

    def context(self) -> Dict:
        # Override to add list of rate categories and rate types
        dictionary = super().context()
        dictionary["rate_categories"] = RateCategory.objects.all()
        dictionary["rate_types"] = RateType.objects.all().order_by("-type")
        dictionary["tools"] = Tool.objects.all()
        dictionary["rate_list_excluded_tools"] = Tool.objects.filter(
            id__in=self.get_list_int("rates_rate_list_excluded_tools")
        )
        return dictionary

    def validate(self, name, value):
        if name == "rates_rate_list_page_show_categories" and value:
            validate_comma_separated_integer_list(value)
        if name == "rates_rate_list_page_show_types" and value:
            validate_comma_separated_integer_list(value)
        if name == "rates_rate_list_excluded_tools" and value:
            validate_comma_separated_integer_list(value)

    def save(self, request, element=None):
        errors = super().save(request, element)

        show_types = ",".join(request.POST.getlist("rates_rate_list_page_show_types_list", []))
        try:
            self.validate("rates_rate_list_page_show_types", show_types)
            type(self).set("rates_rate_list_page_show_types", show_types)
        except (ValidationError, InvalidCustomizationException) as e:
            errors["rates_rate_list_page_show_types"] = {"error": str(e.message or e.msg), "value": show_types}

        show_categories = ",".join(request.POST.getlist("rates_rate_list_page_show_categories_list", []))
        try:
            self.validate("rates_rate_list_page_show_categories", show_categories)
            type(self).set("rates_rate_list_page_show_categories", show_categories)
        except (ValidationError, InvalidCustomizationException) as e:
            errors["rates_rate_list_page_show_categories"] = {
                "error": str(e.message or e.msg),
                "value": show_categories,
            }

        exclude_tools = ",".join(request.POST.getlist("rate_list_excluded_tool_list", []))
        try:
            self.validate("rates_rate_list_excluded_tools", exclude_tools)
            type(self).set("rates_rate_list_excluded_tools", exclude_tools)
        except (ValidationError, InvalidCustomizationException) as e:
            errors["rates_rate_list_excluded_tools"] = {"error": str(e.message or e.msg), "value": exclude_tools}

        if not errors:
            from NEMO.rates import rate_class

            rate_class.load_rates()
        return errors
