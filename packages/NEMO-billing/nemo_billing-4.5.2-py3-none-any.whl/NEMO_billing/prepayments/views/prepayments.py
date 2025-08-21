import datetime
from typing import Set

from NEMO.decorators import accounting_or_user_office_or_manager_required
from NEMO.typing import QuerySetType
from NEMO.utilities import extract_optional_beginning_and_end_dates, get_month_timeframe, month_list
from NEMO.views.pagination import SortedPaginator
from NEMO.views.usage import get_managed_projects
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from NEMO_billing.models import CoreFacility
from NEMO_billing.prepayments.models import Fund, ProjectPrepaymentDetail
from NEMO_billing.utilities import get_charges_amount_between, number_of_months_between_dates


@login_required
def usage_project_prepayments(request):
    start_date, end_date = get_month_timeframe()
    projects = get_managed_projects(request.user)
    prepaid_projects = ProjectPrepaymentDetail.objects.filter(
        project__in=[project for project in projects if project.active]
    )
    add_fund_info_to_prepaid_projects(request, prepaid_projects, start_date)
    return render(request, "prepayments/prepaid_project_status_table.html", {"page": prepaid_projects})


@accounting_or_user_office_or_manager_required
@require_http_methods(["GET", "POST"])
def prepaid_project_status(request):
    # Default is year to date
    start_date, end_date = get_month_timeframe()
    start_date = start_date.replace(month=1)
    if request.GET.get("start"):
        submitted_start_date, submitted_end_date = extract_optional_beginning_and_end_dates(request.GET, date_only=True)
        if submitted_start_date:
            start_date = start_date.replace(year=submitted_start_date.year, month=submitted_start_date.month)
    page = SortedPaginator(ProjectPrepaymentDetail.objects.all(), request, order_by="project").get_current_page()
    add_fund_info_to_prepaid_projects(request, page.object_list, start_date)
    dictionary = {
        "start": start_date,
        "month_list": month_list(),
        "page": page,
        "core_facilities_exist": CoreFacility.objects.exists(),
    }
    return render(request, "prepayments/prepaid_project_status.html", dictionary)


def add_fund_info_to_prepaid_projects(request, prepaid_projects: QuerySetType[ProjectPrepaymentDetail], start_date):
    for prepaid_project in prepaid_projects:
        try:
            charges, charges_amount, funds = get_prepayment_info_for_status(prepaid_project, start_date)
            prepaid_project.total_funds = sum(fund.amount for fund in funds)
            prepaid_project.balance = sum(fund.balance for fund in funds)
            prepaid_project.charges_amount = sum(charge.amount for charge in charges)
            prepaid_project.taxes_amount = (
                prepaid_project.charges_amount * prepaid_project.configuration.tax_amount()
                if not prepaid_project.project.projectbillingdetails.no_tax
                else 0
            )
            prepaid_project.total_charges_amount = prepaid_project.charges_amount + prepaid_project.taxes_amount
            prepaid_project.total_funds_left = prepaid_project.balance - prepaid_project.total_charges_amount
            prepaid_project.charges = charges
            prepaid_project.charges.reverse()
        except Exception as e:
            messages.error(request, str(e), extra_tags="data-trigger=manual")


def get_prepayment_info_for_status(prepaid_project: ProjectPrepaymentDetail, fund_start_date):
    # Returns total charges, total charges amount since last updated, and all active funds since fund_start_date
    until = datetime.date.today()
    # Balance last updated is last day of previous month, so start first day of next month
    start_in_month = (prepaid_project.balance_last_updated + relativedelta(months=1)).replace(day=1)
    charges, charges_amount = get_charges_amount_between(
        prepaid_project.project, prepaid_project.configuration, start_in_month, until
    )
    # Check funds month to month
    funds: Set[Fund] = set()
    months = number_of_months_between_dates(until, fund_start_date)
    for month in range(0, months + 1):
        month_date = fund_start_date + relativedelta(months=month)
        # beginning and end of the month
        start, end = get_month_timeframe(month_date.isoformat())
        # only need to check funds valid at this date (expired or inactive won't be returned by active_funds)
        try:
            new_funds: QuerySetType[Fund] = prepaid_project.active_funds(end.date(), include_zero_balance=True)
            funds.update(new_funds)
        except Exception:
            pass
    charges.sort(key=lambda x: x.start)
    return charges, charges_amount, funds
