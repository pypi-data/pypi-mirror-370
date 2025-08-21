from typing import Dict

from NEMO.decorators import customization
from NEMO.exceptions import InvalidCustomizationException
from NEMO.models import Tool
from NEMO.views.customization import CustomizationBase
from django.core.exceptions import ValidationError
from django.core.validators import validate_comma_separated_integer_list, validate_integer

from NEMO_billing.cap_discount.models import CAPDiscountConfiguration
from NEMO_billing.invoices.models import BillableItemType


@customization(key="cap_discount", title="Billing CAP Discounts")
class CAPDiscountCustomization(CustomizationBase):
    variables = {
        "cap_billing_exclude_tools": "",
        "cap_billing_default_billable_types": "",
        "cap_billing_default_interval": "1",
        "cap_billing_default_frequency": "",
    }

    def context(self) -> Dict:
        # Override to add list of tools
        dictionary = super().context()
        dictionary["tools"] = Tool.objects.all()
        dictionary["selected_tools"] = Tool.objects.filter(id__in=self.get_excluded_tool_ids())
        dictionary["billable_types"] = BillableItemType.choices()
        dictionary["selected_billable_types"] = self.get_default_billable_types()
        dictionary["recurrence_frequencies"] = CAPDiscountConfiguration.reset_frequency.field.choices
        return dictionary

    def validate(self, name, value):
        if name in ["cap_billing_exclude_tools", "cap_billing_default_billable_types"] and value:
            validate_comma_separated_integer_list(value)
        if name in ["cap_billing_default_frequency", "cap_billing_default_interval"] and value:
            validate_integer(value)

    def save(self, request, element=None) -> Dict[str, Dict[str, str]]:
        errors = super().save(request, element)
        exclude_tools = ",".join(request.POST.getlist("cap_billing_exclude_tools_list", []))
        try:
            self.validate("cap_billing_exclude_tools", exclude_tools)
            type(self).set("cap_billing_exclude_tools", exclude_tools)
        except (ValidationError, InvalidCustomizationException) as e:
            errors["cap_billing_exclude_tools"] = {"error": str(e.message or e.msg), "value": exclude_tools}
        default_types = ",".join(request.POST.getlist("cap_billing_default_billable_types_list", []))
        try:
            self.validate("cap_billing_default_billable_types", default_types)
            type(self).set("cap_billing_default_billable_types", default_types)
        except (ValidationError, InvalidCustomizationException) as e:
            errors["cap_billing_default_billable_types"] = {"error": str(e.message or e.msg), "value": default_types}
        return errors

    @classmethod
    def get_excluded_tool_ids(cls):
        return [int(pk) for pk in cls.get("cap_billing_exclude_tools").split(",") if pk]

    @classmethod
    def get_default_billable_types(cls):
        return [int(value) for value in cls.get("cap_billing_default_billable_types").split(",") if value]
