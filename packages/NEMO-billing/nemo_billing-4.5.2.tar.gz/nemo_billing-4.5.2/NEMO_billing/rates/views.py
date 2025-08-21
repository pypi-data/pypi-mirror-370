from datetime import datetime
from itertools import groupby
from typing import Iterable, List, Tuple

from NEMO.decorators import accounting_or_manager_required, user_passes_test
from NEMO.models import Area, Consumable, Tool
from NEMO.utilities import distinct_qs_value_list, format_datetime
from NEMO.views.pagination import SortedPaginator
from django.conf import settings
from django.db.models import Q, QuerySet
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET, require_http_methods

from NEMO_billing.invoices.utilities import flatten
from NEMO_billing.rates.admin import RateAdminForm
from NEMO_billing.rates.customization import BillingRatesCustomization
from NEMO_billing.rates.models import Rate, RateCategory, RateTime, RateType
from NEMO_billing.rates.utilities import RateHistory

OTHER_RATE_TYPE = "other"


@accounting_or_manager_required
@require_GET
def rates(request, rate_type_choice: str = None):
    rate_type = rate_type_choice or RateType.Type.TOOL
    rate_types = get_rate_types(rate_type)
    rate_order_by = [rate_type.lower(), "type", "category", "time"]
    if rate_type_choice and rate_type_choice.lower() == OTHER_RATE_TYPE:
        rate_types = RateType.objects.filter(item_specific=False)
        rate_order_by = []
    rate_qs = Rate.non_deleted()
    page_qs = rate_qs.filter(type__in=rate_types).order_by(*rate_order_by)
    page = SortedPaginator(page_qs, request, order_by="type" if not rate_order_by else None).get_current_page()
    # remove when fixed in NEMO (allowing no order_type)
    if rate_order_by:
        page.paginator.order_by = ""

    # Creating rates list for search autocomplete
    rate_search = "["
    for tool_id in distinct_qs_value_list(rate_qs.filter(tool__isnull=False), "tool"):
        tool = Tool.objects.get(pk=tool_id)
        rate_search += '{{"name":"{0}", "id":{1}, "type_value": "{2}"}},'.format(
            escape(tool.name), tool_id, RateType.Type.TOOL
        )
    for area_id in distinct_qs_value_list(rate_qs.filter(area__isnull=False), "area"):
        area = Area.objects.get(pk=area_id)
        rate_search += '{{"name":"{0}", "id":{1}, "type_value": "{2}"}},'.format(
            escape(area.name), area_id, RateType.Type.AREA
        )
    for consumable_id in distinct_qs_value_list(rate_qs.filter(consumable__isnull=False), "consumable"):
        consumable = Consumable.objects.get(pk=consumable_id)
        rate_search += '{{"name":"{0}", "id":{1}, "type_value": "{2}"}},'.format(
            escape(consumable.name), consumable_id, RateType.Type.CONSUMABLE
        )
    for rate_type_item in RateType.objects.all():
        if not rate_type_item.item_specific:
            if rate_qs.filter(type=rate_type_item).exists():
                rate_search += '{{"name":"{0}", "id":"{1}", "type_value": "{2}"}},'.format(
                    escape(str(rate_type_item)), "", rate_type_item.get_rate_group_type()
                )
    rate_search = rate_search.rstrip(",") + "]"
    rate_search = mark_safe(rate_search)

    dictionary = {
        "rate_type": rate_type,
        "page": page,
        "show_type": page_qs.values("type").distinct().count() > 1 or rate_type.lower() == OTHER_RATE_TYPE,
        "show_category": page_qs.filter(category__isnull=False).exists(),
        "show_time": page_qs.filter(time__isnull=False).exists(),
        "search_rates": rate_search,
    }

    return render(request, "rates/rates.html", dictionary)


@accounting_or_manager_required
@require_http_methods(["GET", "POST"])
def create_or_modify_rate(request, rate_type_choice=None, item_id=None):
    tool = get_object_or_404(Tool, pk=item_id) if item_id and rate_type_choice == RateType.Type.TOOL else None
    area = get_object_or_404(Area, pk=item_id) if item_id and rate_type_choice == RateType.Type.AREA else None
    consumable = (
        get_object_or_404(Consumable, pk=item_id) if item_id and rate_type_choice == RateType.Type.CONSUMABLE else None
    )

    # All tools, visible or not, should be able to have a rate
    tools = list(Tool.objects.all())
    # Because we are showing tool children, we cannot sort the queryset (child tool has no category)
    tools.sort(key=lambda x: (x.category, x.name))
    rate_types = get_rate_types(rate_type_choice)

    dictionary = {
        "rate_types": rate_types,
        "rate_type_choice": rate_type_choice,
        "item": tool or area or consumable,
        "rate_type_choices": get_rate_type_choices(),
        "rate_categories": RateCategory.objects.all(),
        "rate_times": RateTime.objects.all(),
        "tools": tools,
        "areas": Area.objects.filter(area_children_set__isnull=True),
        "consumables": Consumable.objects.all().order_by("category", "name"),
    }

    if request.method == "GET":
        rate_forms = get_forms_sorted_by_category(request, rate_types, tool, area, consumable)
        dictionary["forms"] = rate_forms
        return render(request, "rates/rate.html", dictionary)
    else:
        rate_form = RateAdminForm(request.POST, rate_history=True)
        if rate_form.is_valid():
            # Don't commit since we want to save it using our own method
            form_rate: Rate = rate_form.save(commit=False)
            form_rate.save_with_user(request.user)
            rate_form.save_m2m()
            # Reinitialize the form now that we know everything went well
            rate_form = init_form(
                request,
                form_rate.type,
                form_rate.flat,
                form_rate.tool,
                form_rate.area,
                form_rate.consumable,
                form_rate.category,
            )
        dictionary["rate_form"] = rate_form
        dictionary["index"] = request.POST.get("index", 0)
        return render(request, "rates/rate_form_details.html", dictionary)


# We are building forms for each rate type, for each category.
# The goal is to have all rate forms related to one group type (Tool, Area, Supply etc.) in one view.
def get_forms_sorted_by_category(
    request, rate_types: QuerySet[RateType], tool, area, consumable
) -> List[RateAdminForm]:
    forms = []
    categories = RateCategory.objects.all()
    missed_reservation_flat = getattr(settings, "DEFAULT_MISSED_RESERVATION_FLAT", True)
    # Create a form for each rate type
    for rate_type in rate_types:
        missed_r_type = rate_type.type in [RateType.Type.TOOL_MISSED_RESERVATION, RateType.Type.AREA_MISSED_RESERVATION]
        default_flat = missed_r_type and missed_reservation_flat or rate_type.type == RateType.Type.CONSUMABLE
        if rate_type.category_specific and categories:
            # Add a form for each category
            for category in categories:
                forms.append(init_form(request, rate_type, default_flat, tool, area, consumable, category))
        else:
            forms.append(init_form(request, rate_type, default_flat, tool, area, consumable))
    forms.sort(key=lambda form: (form.instance.category.name if form.instance.category else ""))
    return forms


def init_form(request, rate_type, flat, tool=None, area=None, consumable=None, category=None) -> RateAdminForm:
    instance = Rate(type=rate_type, category=category, tool=tool, area=area, consumable=consumable, flat=flat)
    return RateAdminForm(
        instance=instance,
        rate_history=True,
    )


def get_rate_type_choices() -> List[Tuple[str, str]]:
    # Since we want to group all tool related types, we only have a subset here
    # Return a list of (value, display value) for use in a select
    rate_type_choices = set()
    for rate_type in RateType.objects.all():
        if rate_type.is_tool_rate() and rate_type.item_specific:
            rate_type_choices.add((RateType.Type.TOOL, RateType.Type.TOOL))
        elif rate_type.is_area_rate() and rate_type.item_specific:
            rate_type_choices.add((RateType.Type.AREA, RateType.Type.AREA))
        elif rate_type.is_consumable_rate() and rate_type.item_specific:
            rate_type_choices.add((rate_type.type, rate_type.get_type_display()))
        else:
            rate_type_choices.add((rate_type.type, rate_type.get_type_display()))
    return sorted(rate_type_choices)


def get_rate_types(rate_type_choice: str) -> QuerySet[RateType]:
    rate_types = RateType.objects.none()
    if rate_type_choice:
        if rate_type_choice == RateType.Type.TOOL:
            rate_types = RateType.objects.filter(
                type__in=[
                    RateType.Type.TOOL_USAGE,
                    RateType.Type.TOOL_MISSED_RESERVATION,
                    RateType.Type.TOOL_TRAINING_INDIVIDUAL,
                    RateType.Type.TOOL_TRAINING_GROUP,
                ],
                item_specific=True,
            )
        elif rate_type_choice == RateType.Type.AREA:
            rate_types = RateType.objects.filter(
                type__in=[RateType.Type.AREA_USAGE, RateType.Type.AREA_MISSED_RESERVATION], item_specific=True
            )
        elif rate_type_choice == RateType.Type.CONSUMABLE:
            rate_types = RateType.objects.filter(type=RateType.Type.CONSUMABLE)
        else:
            rate_types = RateType.objects.filter(type=rate_type_choice)
    return rate_types


@accounting_or_manager_required
@require_GET
def delete_rate_time(request, rate_id):
    rate = get_object_or_404(Rate, pk=rate_id)
    if rate.effective_date and rate.effective_date >= datetime.today().date():
        rate.delete_with_user(request.user)
    else:
        return HttpResponseBadRequest("Past rates cannot be deleted")
    return HttpResponse()


def rate_list_permission(user):
    page_access = BillingRatesCustomization.get("rates_rate_list_page_access")

    return page_access == PageAccess.PUBLIC or (page_access == PageAccess.AUTHENTICATED and user.is_active)


@user_passes_test(rate_list_permission)
@require_GET
def rate_list(request, rate_type_choice: str = None):
    show_zero_rates = BillingRatesCustomization.get_bool("rates_rate_list_show_zero_rates")
    show_types = BillingRatesCustomization.get_list_int("rates_rate_list_page_show_types")
    show_categories = BillingRatesCustomization.get_list_int("rates_rate_list_page_show_categories")
    show_facilities = BillingRatesCustomization.get_bool("rates_rate_list_show_facilities")
    excluded_tools = BillingRatesCustomization.get_list_int("rates_rate_list_excluded_tools")

    show_tools_type = show_rate_type(show_types, RateType.Type.TOOL)
    show_areas_type = show_rate_type(show_types, RateType.Type.AREA)
    show_supplies_type = show_rate_type(show_types, RateType.Type.CONSUMABLE)
    show_other_type = show_rate_type(show_types, OTHER_RATE_TYPE)

    default_rate_type = RateType.Type.TOOL

    # determine default rate_type, no user choice
    if not show_tools_type:
        default_rate_type = RateType.Type.AREA

    if not show_tools_type and not show_areas_type:
        default_rate_type = RateType.Type.CONSUMABLE

    if not show_tools_type and not show_areas_type and not show_supplies_type:
        default_rate_type = OTHER_RATE_TYPE

    # determine default rate_type if user has selected a rate type that is no longer valid
    if not show_tools_type and rate_type_choice == RateType.Type.TOOL:
        rate_type_choice = None

    if not show_areas_type and rate_type_choice == RateType.Type.AREA:
        rate_type_choice = None

    if not show_supplies_type and rate_type_choice == RateType.Type.CONSUMABLE:
        rate_type_choice = None

    if not show_other_type and rate_type_choice == OTHER_RATE_TYPE:
        rate_type_choice = None

    if rate_type_choice not in [RateType.Type.TOOL, RateType.Type.AREA, RateType.Type.CONSUMABLE, OTHER_RATE_TYPE]:
        rate_type_choice = None

    rate_type = rate_type_choice or default_rate_type

    if rate_type == OTHER_RATE_TYPE:
        rate_types = RateType.objects.filter(item_specific=False)
        rate_order_by = []
        has_children = False
    else:
        rate_types = get_rate_types(rate_type)
        rate_order_by = [rate_type.lower(), "type", "category"]
        has_children = rate_types.count() > 1

    if show_types:
        rate_types = rate_types.filter(id__in=show_types)

    # For tool rates, don't display not visible tool rates, unless it's a child tool
    tool_filter = Q(tool__isnull=True) | (
        (Q(tool__visible=True) | Q(tool__parent_tool__isnull=False)) & ~Q(tool__id__in=excluded_tools)
    )
    all_rates = Rate.non_deleted().filter(type__in=rate_types).filter(tool_filter).order_by(*rate_order_by)

    rate_categories = distinct_qs_value_list(all_rates, "category")

    if show_categories:
        rate_categories = [cat_id for cat_id in rate_categories if cat_id in show_categories]

    rate_categories = sorted([RateCategory.objects.get(id=cat_id).name for cat_id in rate_categories if cat_id])

    formatted_rates = []
    last_item = ""
    item_index = 0
    has_empty_category = not RateCategory.objects.exists() or rate_types.filter(category_specific=False).exists()

    if rate_type == OTHER_RATE_TYPE:
        for rate_type_index, group in groupby(all_rates, lambda x: x.type):
            items = list(group)
            item = items[0].get_item()
            is_first = False

            if last_item != item:
                last_item = item
                is_first = True
                item_index += 1

            type_rates = []
            has_rates = False
            if not rate_type_index.category_specific or not RateCategory.objects.exists():
                has_rates = True
                type_rates.append(rate_display_with_details([items[0]], show_zero_rates))
            else:
                if has_empty_category:
                    type_rates.append("")
                for rate_category in rate_categories:
                    tool_rate_category = filter(lambda x: x.category.name == rate_category, items)
                    rate_display = rate_display_with_details(tool_rate_category, show_zero_rates)
                    if rate_display != "":
                        has_rates = True
                    type_rates.append(rate_display)
            if has_rates:
                formatted_rates.append(
                    RateListModel("", item, rate_type_index, is_first, item_index, has_children, type_rates)
                )

    else:
        for category_type_index, group in groupby(all_rates, lambda x: x.get_item()):
            items = list(group)
            has_children = len(list(groupby(items, lambda x: x.type))) > 1
            facility = ""
            if show_facilities:
                facility = category_type_index.core_facility

            item_index += 1
            if rate_types.count() > 1:
                is_first = True
                for item_rate_type in rate_types:
                    item_rates = []
                    has_rates = False
                    if not item_rate_type.category_specific or not RateCategory.objects.exists():
                        has_rates = True
                        item_rates.append(rate_display_with_details(items, show_zero_rates))
                    else:
                        if has_empty_category:
                            item_rates.append("")
                        for rate_category in rate_categories:
                            tool_rate_category = filter(
                                lambda x: x.category.name == rate_category and x.type == item_rate_type, items
                            )
                            rate_display = rate_display_with_details(tool_rate_category, show_zero_rates)
                            if rate_display != "":
                                has_rates = True
                            item_rates.append(rate_display)
                    if has_rates:
                        formatted_rates.append(
                            RateListModel(
                                facility,
                                category_type_index,
                                item_rate_type,
                                is_first,
                                item_index,
                                has_children,
                                item_rates,
                            )
                        )

                    is_first = False

            else:
                items_type = items[0].type
                item_rates = []
                has_rates = False
                if not items_type.category_specific or not RateCategory.objects.exists():
                    has_rates = True
                    item_rates.append(rate_display_with_details(items, show_zero_rates))
                else:
                    if has_empty_category:
                        item_rates.append("")
                    for rate_category in rate_categories:
                        tool_rate_category = filter(lambda x: x.category.name == rate_category, items)
                        rate_display = rate_display_with_details(tool_rate_category, show_zero_rates)
                        if rate_display != "":
                            has_rates = True
                        item_rates.append(rate_display)
                if has_rates:
                    formatted_rates.append(
                        RateListModel(facility, category_type_index, items_type, True, 0, has_children, item_rates)
                    )

    if show_facilities:
        formatted_rates.sort(key=lambda a: a.facility.name if a.facility else "")

    # boolean to toggle rate type column in table
    has_multiple_rate_types = rate_types.count() > 1

    dictionary = {
        "rate_type": rate_type,
        "formatted_rates": formatted_rates,
        "rate_categories": rate_categories,
        "has_empty_category": has_empty_category,
        "show_tools_type": show_tools_type,
        "show_areas_type": show_areas_type,
        "show_supplies_type": show_supplies_type,
        "show_other_type": show_other_type,
        "has_multiple_rate_types": has_multiple_rate_types,
        "item_label": "Item" if has_multiple_rate_types or not rate_types.exists() else f"{rate_types[0]} rates",
    }

    return render(request, "rates/rate_list.html", dictionary)


def rate_display_with_details(item_rates: Iterable[Rate], show_zero_rates):
    rate_display = ""

    current_and_future_rates = RateHistory(item_rates, datetime.today().date()).current_and_future_rates().values()
    current_and_future_rates = flatten(current_and_future_rates)
    for item_rate in current_and_future_rates:
        if item_rate.amount != 0 or show_zero_rates:
            rate_display += f"{item_rate.display_rate()}{' (' + item_rate.time.name + ')' if item_rate.time else ''}"
            if item_rate.effective_date and item_rate.effective_date > datetime.today().date():
                rate_display += f" (effective {format_datetime(item_rate.effective_date, 'SHORT_DATE_FORMAT')})"
            rate_display += "<br/>"

    return rate_display


def show_rate_type(show_rate_types, parent_rate_type):
    if not show_rate_types:
        return True

    if not parent_rate_type == OTHER_RATE_TYPE:
        rate_types = get_rate_types(parent_rate_type)
    else:
        rate_types = RateType.objects.filter(item_specific=False)
    return rate_types.filter(id__in=show_rate_types).exists()


class RateListModel:
    def __init__(self, facility, item, rate_type, is_first, item_index, has_children, item_rates):
        self.facility = facility
        self.item = item
        self.rate_type = rate_type
        self.is_first = is_first
        self.item_index = item_index
        self.has_children = has_children
        self.rates = item_rates


class PageAccess(object):
    PUBLIC = "public"
    AUTHENTICATED = "auth"
