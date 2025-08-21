from collections import defaultdict
from decimal import Decimal
from logging import getLogger
from typing import Dict, List

from NEMO.decorators import accounting_or_user_office_or_manager_required, any_staff_required
from NEMO.models import Account, AccountType, AdjustmentRequest, Project, ProjectType, User
from NEMO.utilities import (
    BasicDisplayTable,
    export_format_datetime,
    format_datetime,
    get_day_timeframe,
    get_month_timeframe,
)
from NEMO.views.customization import AdjustmentRequestsCustomization
from NEMO.views.usage import date_parameters_dictionary, get_managed_projects, get_project_applications
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from NEMO_billing.customization import BillingCustomization
from NEMO_billing.invoices.models import InvoiceConfiguration, InvoiceDetailItem
from NEMO_billing.invoices.processors import BillableItem, invoice_data_processor_class as data_processor
from NEMO_billing.invoices.utilities import display_amount
from NEMO_billing.templatetags.billing_tags import cap_discount_installed

logger = getLogger(__name__)


@login_required
@require_GET
def user_usage(request):
    user: User = request.user
    user_managed_projects = get_managed_projects(user)
    customer_filter = Q(customer=user) | Q(project__in=user_managed_projects)
    user_filter = Q(user=user) | Q(project__in=user_managed_projects)
    trainee_filter = Q(trainee=user) | Q(project__in=user_managed_projects)
    csv_export = bool(request.GET.get("csv", False))
    show_only_my_usage = user_managed_projects and request.GET.get("show_only_my_usage", "enabled") == "enabled"
    if show_only_my_usage:
        # Forcing to be user only
        customer_filter &= Q(customer=user)
        user_filter &= Q(user=user)
        trainee_filter &= Q(trainee=user)
    return usage(
        request,
        usage_filter=user_filter,
        area_access_filter=customer_filter,
        staff_charges_filter=customer_filter,
        consumable_filter=customer_filter,
        reservation_filter=user_filter,
        training_filter=trainee_filter,
        custom_charges_filter=customer_filter,
        show_only_my_usage=show_only_my_usage,
        csv_export=csv_export,
        user_managed_projects=user_managed_projects,
    )


@any_staff_required
@require_GET
def staff_usage(request):
    user: User = request.user
    usage_filter = Q(operator=user) & ~Q(user=F("operator"))
    area_access_filter = Q(staff_charge__staff_member=user)
    staff_charges_filter = Q(staff_member=user)
    consumable_filter = Q(merchant=user)
    user_filter = Q(pk__in=[])
    trainee_filter = Q(trainer=user)
    custom_charges_filter = Q(creator=user)
    csv_export = bool(request.GET.get("csv", False))
    return usage(
        request,
        usage_filter=usage_filter,
        area_access_filter=area_access_filter,
        staff_charges_filter=staff_charges_filter,
        consumable_filter=consumable_filter,
        reservation_filter=user_filter,
        training_filter=trainee_filter,
        custom_charges_filter=custom_charges_filter,
        show_only_my_usage=None,
        csv_export=csv_export,
        user_managed_projects=set(),
    )


def usage(
    request,
    usage_filter,
    area_access_filter,
    staff_charges_filter,
    consumable_filter,
    reservation_filter,
    training_filter,
    custom_charges_filter,
    show_only_my_usage,
    csv_export,
    user_managed_projects,
):
    user = request.user
    base_dictionary, start, end, kind, identifier = date_parameters_dictionary(request, get_month_timeframe)
    base_dictionary["run_data_collapse"] = set_run_data_collapse(request)
    project_id = request.GET.get("project") or request.GET.get("pi_project")
    if user_managed_projects:
        base_dictionary["selected_project"] = "all"
    if project_id:
        project = get_object_or_404(Project, id=project_id)
        if request.GET.get("project"):
            base_dictionary["selected_user_project"] = project
        else:
            base_dictionary["selected_project"] = project
            base_dictionary["explicitly_display_customer"] = True
        area_access_filter &= Q(project=project)
        staff_charges_filter &= Q(project=project)
        usage_filter &= Q(project=project)
        consumable_filter &= Q(project=project)
        reservation_filter &= Q(project=project)
        training_filter &= Q(project=project)
        custom_charges_filter &= Q(project=project)
    config = InvoiceConfiguration.first_or_default()
    detailed_items = sorted_billable_items(
        start,
        end,
        config,
        usage_filter,
        area_access_filter,
        staff_charges_filter,
        consumable_filter,
        reservation_filter,
        training_filter,
        custom_charges_filter,
    )
    if csv_export:
        return csv_export_response(detailed_items)
    else:
        non_waived_items = [item for item in detailed_items if not item.waived]
        total_charges = Decimal(sum(item.billable_amount for item in non_waived_items))
        dictionary = {
            "detailed_items": detailed_items,
            "total_charges": display_amount(total_charges, config),
            "can_export": True,
            "adjustment_time_limit": AdjustmentRequestsCustomization.get_date_limit(),
            "existing_adjustments": get_existing_adjustments(user),
            "charges_projects": Project.objects.filter(
                id__in=set(
                    list(user.active_projects().values_list("id", flat=True))
                    + list({item.project.id for item in detailed_items if item.project})
                )
            ),
        }
        if BillingCustomization.get_bool("billing_usage_show_pending_vs_final"):
            dictionary["pending_charges"] = display_amount(
                total_charges - sum(item.invoiced_amount or 0 for item in non_waived_items), config
            )
        if user_managed_projects:
            dictionary["pi_projects"] = user_managed_projects
            dictionary["show_only_my_usage"] = show_only_my_usage
        dictionary["no_charges"] = not dictionary["detailed_items"]
        if cap_discount_installed():
            from NEMO_billing.cap_discount.models import CAPDiscount

            if CAPDiscount.objects.filter(user=user).exists():
                dictionary["cap_discounts_url"] = reverse("usage_cap_discounts")
        if user_managed_projects and any(
            [getattr(project, "projectprepaymentdetail", None) for project in user_managed_projects if project.active]
        ):
            dictionary["project_prepayments_url"] = reverse("usage_project_prepayments")

        return render(request, "invoices/usage.html", {**base_dictionary, **dictionary})


@accounting_or_user_office_or_manager_required
@require_GET
def project_usage(request):
    base_dictionary, start, end, kind, identifier = date_parameters_dictionary(request, get_day_timeframe)
    base_dictionary["run_data_collapse"] = set_run_data_collapse(request)

    detailed_items: List[BillableItem] = []
    config = InvoiceConfiguration.first_or_default()

    projects = []
    user = None
    account = None
    selection = ""

    # Get selection as strings.
    selected_account_type = request.GET.get("account_type")
    selected_project_type = request.GET.get("project_type")

    try:
        if kind == "projectapplication":
            projects = Project.objects.filter(application_identifier=identifier)
            selection = identifier
        elif kind == "project":
            projects = [Project.objects.get(id=identifier)]
            selection = projects[0].name
        elif kind == "account":
            account = Account.objects.get(id=identifier)
            projects = Project.objects.filter(account=account)
            selection = account.name
        elif kind == "user":
            user = User.objects.get(id=identifier)
            projects = user.active_projects()
            selection = str(user)

        customer_filter = Q()
        user_filter = Q()
        trainee_filter = Q()
        if projects:
            customer_filter = customer_filter & Q(project__in=projects)
            user_filter = user_filter & Q(project__in=projects)
            trainee_filter = trainee_filter & Q(project__in=projects)
        if user:
            customer_filter = customer_filter & Q(customer=user)
            user_filter = user_filter & Q(user=user)
            trainee_filter = trainee_filter & Q(trainee=user)
        if selected_account_type:
            # Get a subset of projects and filter the other records using that subset.
            projects_by_account_type = Project.objects.filter(account__type__id=selected_account_type)
            customer_filter = customer_filter & Q(project__in=projects_by_account_type)
            user_filter = user_filter & Q(project__in=projects_by_account_type)
            trainee_filter = trainee_filter & Q(project__in=projects_by_account_type)
        if selected_project_type:
            # Get a subset of projects and filter the other records using that subset.
            projects_by_type = Project.objects.filter(project_types__id=selected_project_type)
            customer_filter = customer_filter & Q(project__in=projects_by_type)
            user_filter = user_filter & Q(project__in=projects_by_type)
            trainee_filter = trainee_filter & Q(project__in=projects_by_type)
        detailed_items = sorted_billable_items(
            start,
            end,
            config,
            usage_filter=user_filter,
            area_access_filter=customer_filter,
            staff_charges_filter=customer_filter,
            consumable_filter=customer_filter,
            reservation_filter=user_filter,
            training_filter=trainee_filter,
            custom_charges_filter=customer_filter,
        )
        if bool(request.GET.get("csv", False)):
            return csv_export_response(detailed_items)
    except Exception as e:
        logger.exception(e)

    # Get a list of unique account types for the dropdown field.
    account_types = AccountType.objects.filter(id__in=Account.objects.values_list("type__id", flat=True))

    # Get a list of unique project types for the dropdown field.
    project_types = ProjectType.objects.filter(id__in=Project.objects.values_list("project_types__id", flat=True))

    non_waived_items = [item for item in detailed_items if not item.waived]
    total_charges = Decimal(sum(item.billable_amount for item in non_waived_items))
    dictionary = {
        "search_items": set(Account.objects.all())
        | set(Project.objects.all())
        | set(get_project_applications())
        | set(User.objects.filter(is_active=True)),
        "detailed_items": detailed_items,
        "total_charges": display_amount(total_charges, config),
        "pending_charges": display_amount(
            total_charges - sum(item.invoiced_amount or 0 for item in non_waived_items), config
        ),
        "project_autocomplete": True,
        "adjustment_time_limit": AdjustmentRequestsCustomization.get_date_limit(),
        "existing_adjustments": get_existing_adjustments(request.user),
        "selection": selection,
        "can_export": True,
        "account_types": account_types,
        "selected_account_type": selected_account_type,
        "project_types": project_types,
        "selected_project_type": selected_project_type,
    }
    dictionary["no_charges"] = not dictionary["detailed_items"]
    if cap_discount_installed():
        from NEMO_billing.cap_discount.models import CAPDiscount

        if user and CAPDiscount.objects.filter(user=user).exists():
            dictionary["cap_discounts_url"] = reverse("usage_cap_discounts_user", args=[identifier])
        if account and CAPDiscount.objects.filter(account=account).exists():
            dictionary["cap_discounts_url"] = reverse("usage_cap_discounts_account", args=[identifier])
    return render(request, "invoices/usage.html", {**base_dictionary, **dictionary})


def sorted_billable_items(
    start,
    end,
    config,
    usage_filter,
    area_access_filter,
    staff_charges_filter,
    consumable_filter,
    reservation_filter,
    training_filter,
    custom_charges_filter,
) -> List[BillableItem]:
    items = data_processor.get_billable_items_with_charge_filters(
        start,
        end,
        config,
        usage_filter,
        area_access_filter,
        staff_charges_filter,
        consumable_filter,
        reservation_filter,
        training_filter,
        custom_charges_filter,
        False,
    )
    augment_with_invoice_items(items)
    items.sort(key=lambda x: (-x.item_type.value, x.start), reverse=True)
    return items


def augment_with_invoice_items(billables: List[BillableItem]):
    pending_vs_final = BillingCustomization.get_bool("billing_usage_show_pending_vs_final")
    # let's get invoice items in one query. We are only using item.id which means
    # we might get a few more than we really need (different types), but it's better than a query for each
    invoice_items: List[InvoiceDetailItem] = list(
        InvoiceDetailItem.objects.filter(
            invoice__voided_date__isnull=True, object_id__in=[billable.item.id for billable in billables]
        )
        .select_related("invoice__configuration", "content_type")
        .only("invoice", "content_type", "object_id", "rate", "amount", "discount", "waived")
    )
    for billable in billables:
        matching_items = [
            invoice_item
            for invoice_item in invoice_items
            if invoice_item.object_id == billable.item.id
            and invoice_item.content_type.model == billable.item._meta.model_name
        ]
        invoice_item: InvoiceDetailItem = matching_items[0] if matching_items else None
        billable.invoiced_display_amount = invoice_item.amount_display() if invoice_item else None
        billable.invoiced_amount = invoice_item.amount if invoice_item else None
        billable.invoiced_discount = invoice_item.discount if invoice_item else None
        billable.invoiced_rate = invoice_item.rate if invoice_item else None
        billable.amount = billable.amount if not billable.invoiced_amount else None
        billable.billable_rate = billable.invoiced_rate or billable.display_rate
        billable.billable_amount = billable.invoiced_amount or billable.amount or 0
        billable.billable_display_amount = billable.invoiced_display_amount or (
            f"{'(pending) ' if pending_vs_final else ''}{billable.display_amount}" if billable.display_amount else ""
        )
        billable.merged_amount = billable.invoiced_amount or billable.amount

        if hasattr(billable, "rate") and billable.rate:
            if billable.rate.daily:
                billable.unit_type = "daily"
            elif billable.rate.flat:
                billable.unit_type = "flat"
            else:
                billable.unit_type = "hourly"
        else:
            billable.unit_type = None

        if billable.unit_type == "hourly" and billable.quantity is not None:
            # Convert quantity from minutes to hours.
            billable.unit_quantity = Decimal(billable.quantity / 60).quantize(Decimal("0.01"))
        elif billable.unit_type == "flat" and billable.quantity is not None:
            # Set quantity to 1.
            billable.unit_quantity = 1
        elif billable.unit_type == "daily" and billable.quantity is not None:
            # First usage in the day gets a billable.amount, but subsequent check-outs in the same day will have `billable.amount` = 0.
            # Check-outs spanning multiple days are given separate `billable` datasets, one per day with the appropriate charge amount,
            # if `billable.rate.daily_split_multi_day_charges` is true.
            billable.unit_quantity = 1 if billable.amount > 0 else 0
        else:
            # Otherwise, keep the quantity value (could be None)
            # Getting here means the `billable.unit_type` is not accounted for.
            billable.unit_quantity = billable.quantity


def csv_export_response(detailed_items: List[BillableItem]):
    table_result = BasicDisplayTable()
    table_result.add_header(("type", "Type"))
    table_result.add_header(("user", "User"))
    table_result.add_header(("username", "Username"))
    table_result.add_header(("name", "Item"))
    table_result.add_header(("project", "Project"))
    table_result.add_header(("start", "Start time"))
    table_result.add_header(("end", "End time"))
    table_result.add_header(("quantity", "Quantity"))
    table_result.add_header(("rate", "Rate"))
    table_result.add_header(("cost", "Cost"))
    table_result.add_header(("waived", "Waived"))
    pending_vs_final = BillingCustomization.get_bool("billing_usage_show_pending_vs_final")
    if pending_vs_final:
        table_result.add_header(("cost_pending", "Cost (Pending)"))
    for billable_item in detailed_items:
        billable_dict = {
            "type": billable_item.item_type.display_name(),
            "user": billable_item.user.get_name(),
            "username": billable_item.user.username,
            "name": billable_item.name,
            "project": billable_item.project.name if billable_item.project else "",
            "start": format_datetime(billable_item.start, "SHORT_DATETIME_FORMAT"),
            "end": format_datetime(billable_item.end, "SHORT_DATETIME_FORMAT"),
            "quantity": billable_item.quantity,
            "rate": billable_item.invoiced_rate or (billable_item.rate.display_rate() if billable_item.rate else ""),
            "cost": round(billable_item.invoiced_amount, 2) if billable_item.invoiced_amount else "",
            "waived": billable_item.waived,
        }
        if pending_vs_final:
            billable_dict["cost_pending"] = round(billable_item.amount, 2) if billable_item.amount else ""
        else:
            billable_dict["cost"] = round(billable_item.merged_amount, 2) if billable_item.merged_amount else ""
        table_result.add_row(billable_dict)
    response = table_result.to_csv()
    filename = f"usage_export_{export_format_datetime()}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def get_existing_adjustments(user) -> Dict[int, List]:
    existing_adjustments = defaultdict(list)
    for values in (
        AdjustmentRequest.objects.filter(deleted=False, creator=user).values("item_type", "item_id").distinct()
    ):
        existing_adjustments[values["item_type"]].append(values["item_id"])
    return existing_adjustments


# Remove when NEMO 7.2.0 is released
def set_run_data_collapse(request):
    if request.GET.get("run_data_collapse"):
        request.session["run_data_collapse"] = request.GET.get("run_data_collapse") == "true"
    run_data_collapse = False
    if "run_data_collapse" in request.session:
        run_data_collapse = request.session["run_data_collapse"]
    return run_data_collapse
