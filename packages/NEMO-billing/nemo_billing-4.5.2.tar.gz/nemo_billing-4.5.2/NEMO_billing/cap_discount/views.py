from operator import itemgetter
from typing import Iterable

from NEMO.decorators import accounting_or_user_office_or_manager_required
from NEMO.models import Account, User
from NEMO.typing import QuerySetType
from NEMO.views.pagination import SortedPaginator
from NEMO.views.usage import date_parameters_dictionary
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from NEMO_billing.cap_discount.models import CAPDiscount, CAPDiscountConfiguration


# Custom paginator to handle python sorting (rather than queryset sorting)
class CustomSortedPaginator(SortedPaginator):
    def __init__(self, object_list, request, order_by=None, force_order_by=False):
        self.order_by = order_by if force_order_by else request.GET.get("o", order_by)
        if object_list and isinstance(object_list, QuerySet) and self.order_by:
            object_list = object_list.order_by(self.order_by)
        elif object_list and isinstance(object_list, Iterable) and self.order_by:
            order_attr = (lambda x: itemgetter(self.order_by)) if isinstance(self.order_by, str) else self.order_by
            object_list = sorted(object_list, key=order_attr)
        super().__init__(object_list, request)


@login_required
def usage_cap_discounts(request, user=None):
    if not user:
        user = request.user
    base_dictionary, start, end, kind, identifier = date_parameters_dictionary(request)
    base_dictionary["cap_discounts"] = CAPDiscount.objects.filter(user=user)
    return render(request, "cap_discount/usage_cap_discounts.html", base_dictionary)


@accounting_or_user_office_or_manager_required
@login_required
def usage_cap_discounts_user(request, user_id):
    return usage_cap_discounts(request, get_object_or_404(User, pk=user_id))


@accounting_or_user_office_or_manager_required
def usage_cap_discounts_account(request, account_id):
    base_dictionary, start, end, kind, identifier = date_parameters_dictionary(request)
    base_dictionary["cap_discounts"] = CAPDiscount.objects.filter(account=get_object_or_404(Account, pk=account_id))
    return render(request, "cap_discount/usage_cap_discounts.html", base_dictionary)


@accounting_or_user_office_or_manager_required
@require_http_methods(["GET", "POST"])
def cap_discount_status(request, configuration_id=None):
    configurations: QuerySetType[CAPDiscountConfiguration] = CAPDiscountConfiguration.objects.all()
    filter_configuration = (
        configurations.first()
        if configurations.count() == 1
        else CAPDiscountConfiguration.objects.filter(pk=configuration_id).first()
    )
    order_by: str = request.GET.get("o")
    cap_list = CAPDiscount.objects.all().prefetch_related(
        "account", "user", "capdiscountamount_set", "configuration", "capdiscounttier_set"
    )
    if filter_configuration and cap_list:
        cap_list = cap_list.filter(configuration=filter_configuration)
    if order_by in ["-current_level_reached", "current_level_reached"]:
        # Force list and force sorting here since we cannot use queryset for sorting when including current charges
        page = CustomSortedPaginator(
            list(cap_list), request, order_by=sort_cap_function(reverse=order_by.startswith("-")), force_order_by=True
        ).get_current_page()
    else:
        page = SortedPaginator(cap_list, request, order_by="configuration").get_current_page()

    dictionary = {
        "page": page,
        "selected_configuration": filter_configuration,
        "configurations": configurations,
    }
    return render(
        request,
        "cap_discount/cap_discount_status.html",
        dictionary,
    )


def sort_cap_function(reverse=False):
    sort_min, sort_max = -1, 99999

    def sort_cap_discount(cap_discount: CAPDiscount) -> int:
        current_cap_level = cap_discount.current_level_reached()
        cap_level_list = (
            cap_discount.capdiscounttier_set.all().reverse() if reverse else cap_discount.capdiscounttier_set.all()
        )
        return (
            list(cap_level_list).index(current_cap_level) if current_cap_level else (sort_max if reverse else sort_min)
        )

    return sort_cap_discount
