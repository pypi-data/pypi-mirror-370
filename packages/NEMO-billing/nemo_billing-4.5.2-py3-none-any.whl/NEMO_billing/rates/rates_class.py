from datetime import datetime
from itertools import groupby
from typing import Dict, Iterable, List

from NEMO.models import Consumable, Tool, User
from NEMO.rates import Rates
from NEMO.utilities import distinct_qs_value_list, format_datetime
from django.conf import settings
from django.db.models import Q
from django.utils.formats import number_format

from NEMO_billing.invoices.models import InvoiceConfiguration
from NEMO_billing.invoices.processors import get_rate_with_currency
from NEMO_billing.invoices.utilities import flatten
from NEMO_billing.rates.models import Rate, RateCategory, RateType
from NEMO_billing.rates.utilities import RateHistory, get_rate_history


class DatabaseRates(Rates):

    expand_rates_table = False

    def __init__(self):
        self.currency = getattr(settings, "RATE_CURRENCY", "$")
        self.configuration = InvoiceConfiguration.first_or_default()

    def load_rates(self, force_reload=False):
        super().load_rates(force_reload=force_reload)

    def get_consumable_rates(self, consumables: List[Consumable], user: User = None) -> Dict[str, str]:
        from NEMO_billing.rates.customization import BillingRatesCustomization

        if BillingRatesCustomization.get_bool("rates_hide_consumable_rates"):
            return {}

        # Initialize consumable rates loading before looking up individual rates
        self.configuration.init_rate_help(Q(type__in=RateType.objects.filter(type=RateType.Type.CONSUMABLE)))

        return {consumable.name: self.get_consumable_rate(consumable, user) for consumable in consumables}

    def get_consumable_rate(self, consumable: Consumable, user: User = None) -> str:
        from NEMO_billing.rates.customization import BillingRatesCustomization

        today = datetime.today().date()

        if BillingRatesCustomization.get_bool("rates_hide_consumable_rates"):
            return ""

        consumable_rates = get_rate_history(
            self.configuration.rates_types.get(RateType.Type.CONSUMABLE).id,
            self.configuration.all_rates,
            consumable_id=consumable.id,
            as_of_date=today,
        ).current_and_future_rates()

        consumable_rates = flatten(consumable_rates.values())

        cons_rate_display_list = []
        for cons_rate in consumable_rates:
            cons_rate_display = self.consumable_rate_display(cons_rate)
            if cons_rate.effective_date and cons_rate.effective_date > today:
                cons_rate_display += (
                    f" <b>effective {format_datetime(cons_rate.effective_date, 'SHORT_DATE_FORMAT')}</b>"
                )
            cons_rate_display_list.append(cons_rate_display)

        return ", ".join(cons_rate_display_list) if cons_rate_display_list else ""

    def get_tool_rates(self, tools: List[Tool], user: User = None) -> Dict[str, str]:
        from NEMO_billing.rates.customization import BillingRatesCustomization

        if BillingRatesCustomization.get_bool("rates_hide_table"):
            return {}
        return super().get_tool_rates(tools, user)

    def get_tool_rate(self, tool: Tool, user: User = None) -> str:
        from NEMO_billing.rates.customization import BillingRatesCustomization

        if BillingRatesCustomization.get_bool("rates_hide_table"):
            return ""
        all_tool_rates = Rate.non_deleted().filter(tool=tool).order_by("type", "category")
        if not all_tool_rates:
            return ""
        show_all_categories = BillingRatesCustomization.get_bool("rates_show_all_categories")
        if user and not user.is_any_part_of_staff and not show_all_categories and RateCategory.objects.exists():
            user_categories = distinct_qs_value_list(
                user.active_projects().filter(projectbillingdetails__category__isnull=False),
                "projectbillingdetails__category",
            )
            if not user_categories:
                return ""
            all_tool_rates = all_tool_rates.filter(category__in=user_categories)
        list_by_type = groupby(all_tool_rates, key=lambda x: x.type)
        rate_categories = distinct_qs_value_list(all_tool_rates, "category")
        rate_categories = sorted([RateCategory.objects.get(id=cat_id).name for cat_id in rate_categories if cat_id])
        html_rate = f'<div class="media"><a onclick="toggle_details(this)" class="pointer collapsed" data-toggle="collapse" data-target="#rates_details"><span class="glyphicon glyphicon-list-alt pull-left notification-icon primary-highlight"></span><span class="glyphicon pull-left chevron glyphicon-chevron-{"down" if self.get_expand_rates_table() else "right"}"></span></a>'
        html_rate += f'<div class="media-body"><span class="media-heading">Rates</span><div id="rates_details" class="collapse {"in" if self.get_expand_rates_table() else ""}"><table class="table table-bordered table-hover thead-light" style="width: auto !important; margin-bottom: 0">'
        if rate_categories:
            html_rate += '<tr><th class="text-center"></th><th class="text-center">'
            html_rate += '</th><th class="text-center">'.join(rate_categories)
            html_rate += "</tr>"
        for rate_type, tool_rates in list_by_type:
            html_rate += (
                f'<tr><th class="text-center" style="vertical-align: middle">{rate_type.get_type_display()}</th>'
            )
            if not rate_type.category_specific or not RateCategory.objects.exists():
                html_rate += f'<td class="text-center" style="vertical-align: middle" colspan="{len(rate_categories)}">{self.tool_rate_display_with_details(tool_rates)}</td>'
            else:
                for rate_category in rate_categories:
                    tool_rate_category = all_tool_rates.filter(type=rate_type, category__name=rate_category)
                    html_rate += f'<td class="text-center" style="vertical-align: middle">{self.tool_rate_display_with_details(tool_rate_category)}</td>'
        html_rate += "</tr></table></div></div></div>"
        return html_rate

    def tool_rate_display_with_details(self, rates: Iterable[Rate]):
        today = datetime.today().date()

        display_rates = flatten(RateHistory(rates, today).current_and_future_rates().values())

        return "<br>".join(
            [
                f"{get_rate_with_currency(self.configuration, rate.display_rate())}{' (' + rate.time.name + ')' if rate.time else ''}{' <b>effective '+format_datetime(rate.effective_date, 'SHORT_DATE_FORMAT') + '</b>' if rate.effective_date and rate.effective_date > today else ''}"
                for rate in display_rates
            ]
        )

    def consumable_rate_display(self, rate: Rate) -> str:
        return f"<b>{self.display_amount(rate.amount)}</b>"

    def display_amount(self, amount):
        return f"{self.currency}{number_format(amount, decimal_pos=2)}"
