from decimal import Decimal
from http import HTTPStatus
from typing import Dict, List

from NEMO.decorators import (
    accounting_or_user_office_or_manager_required,
    any_staff_required,
    replace_function,
    staff_member_required,
    synchronized,
)
from NEMO.exceptions import ProjectChargeException
from NEMO.models import Project, StaffCharge, Tool, User
from NEMO.policy import policy_class as policy
from NEMO.typing import QuerySetType
from NEMO.utilities import render_combine_responses
from NEMO.views import api_billing
from NEMO.views.get_projects import get_projects
from NEMO.views.pagination import SortedPaginator
from NEMO.views.remote_work import staff_charges
from NEMO.views.tool_control import enable_tool
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from NEMO_billing.admin import CustomChargeAdminForm, save_or_delete_core_facility
from NEMO_billing.invoices.models import Invoice, InvoiceDetailItem
from NEMO_billing.models import CoreFacility, CoreRelationship, CustomCharge, InstitutionType


@accounting_or_user_office_or_manager_required
@require_http_methods(["GET", "POST"])
def custom_charges(request):
    page = SortedPaginator(CustomCharge.objects.all(), request, order_by="-date").get_current_page()
    core_facilities_exist = CoreFacility.objects.exists()
    return render(
        request, "billing/custom_charges.html", {"page": page, "core_facilities_exist": core_facilities_exist}
    )


@accounting_or_user_office_or_manager_required
@require_http_methods(["GET", "POST"])
def create_or_modify_custom_charge(request, custom_charge_id=None):
    custom_charge = None
    try:
        custom_charge = CustomCharge.objects.get(id=custom_charge_id)
    except CustomCharge.DoesNotExist:
        pass

    form = CustomChargeAdminForm(request.POST or None, instance=custom_charge)

    dictionary = {
        "core_facilities": CoreFacility.objects.all(),
        "core_facility_required": settings.CUSTOM_CHARGE_CORE_FACILITY_REQUIRED,
        "form": form,
        "users": User.objects.filter(is_active=True),
    }
    if request.method == "POST" and form.is_valid():
        charge: CustomCharge = form.save()
        message = f'Your custom charge "{charge.name}" of {charge.amount} for {charge.customer} was successfully logged and will be billed to project {charge.project}.'
        messages.success(request, message=message)
        return redirect("custom_charges")
    else:
        if custom_charge:
            dictionary["projects"] = custom_charge.customer.active_projects()
        if hasattr(form, "cleaned_data") and "customer" in form.cleaned_data:
            dictionary["projects"] = form.cleaned_data["customer"].active_projects()
        return render(request, "billing/custom_charge.html", dictionary)


# Overriding begin staff charge
@staff_member_required
@require_GET
def custom_staff_charges(request):
    staff_member: User = request.user
    staff_charge: StaffCharge = staff_member.get_staff_charge()
    dictionary = dict()
    error = None
    customer = None
    try:
        customer = User.objects.get(id=request.GET["customer"])
    except:
        pass
    if staff_charge:
        return staff_charges(request)
    if customer:
        if customer.active_project_count() > 0:
            dictionary["customer"] = customer
            dictionary["core_facility_id"] = request.GET.get("core_facility")
            if not settings.STAFF_CHARGE_CORE_FACILITY_REQUIRED or dictionary["core_facility_id"]:
                return render(request, "staff_charges/choose_project.html", dictionary)
            else:
                error = "you must select a core facility"
        else:
            error = str(customer) + " does not have any active projects. You cannot bill staff time to this user."
    dictionary["users"] = User.objects.filter(is_active=True).exclude(id=request.user.id)
    dictionary["core_facilities"] = CoreFacility.objects.all()
    dictionary["core_facility_required"] = settings.STAFF_CHARGE_CORE_FACILITY_REQUIRED
    dictionary["error"] = error
    return render(request, "staff_charges/new_custom_staff_charge.html", dictionary)


@staff_member_required
@require_POST
def custom_begin_staff_charge(request):
    if request.user.charging_staff_time():
        return HttpResponseBadRequest("You cannot create a new staff charge when one is already in progress.")
    charge = StaffCharge()
    charge.customer = User.objects.get(id=request.POST["customer"])
    charge.project = Project.objects.get(id=request.POST["project"])
    core_facility = None
    try:
        core_facility = CoreFacility.objects.get(id=request.POST["core_facility"])
        charge.cor_rel = CoreRelationship(core_facility=core_facility, staff_charge=charge)
    except:
        pass
    if settings.STAFF_CHARGE_CORE_FACILITY_REQUIRED and not core_facility:
        return HttpResponseBadRequest("You cannot create a new staff charge without a core facility.")
    # Check if we are allowed to bill to project
    try:
        policy.check_billing_to_project(charge.project, charge.customer, charge, charge)
    except ProjectChargeException as e:
        return HttpResponseBadRequest(e.msg)
    charge.staff_member = request.user
    charge.save()
    if core_facility:
        save_or_delete_core_facility(charge, core_facility, "staff_charge")
    return redirect(reverse("staff_charges"))


# Overriding enable tool
@login_required
@require_POST
@synchronized("tool_id")
def custom_enable_tool(request, tool_id, user_id, project_id, staff_charge):
    response = enable_tool(request, tool_id, user_id, project_id, staff_charge)
    if response.status_code != HTTPStatus.OK:
        return response

    tool = get_object_or_404(Tool, id=tool_id)
    operator: User = request.user
    current_staff_charge = operator.get_staff_charge()
    staff_charge = staff_charge == "true"
    if staff_charge and current_staff_charge and tool.core_facility:
        # set the core facility on the staff charge that was just started by enable_tool()
        save_or_delete_core_facility(current_staff_charge, tool.core_facility, "staff_charge")

    return response


@any_staff_required
@require_GET
def get_projects_for_custom_charges(request):
    return get_projects(request)


@any_staff_required
@require_GET
def email_broadcast(request, audience=""):
    try:
        from NEMO_user_details.views import email as email_views
    except:
        from NEMO.views import email as email_views

    original_response = email_views.email_broadcast(request, audience)

    email_broadcast_dictionary = {}

    if audience == "pi_institution_types":
        email_broadcast_dictionary["institution_types"] = InstitutionType.objects.all()

    return render_combine_responses(
        request,
        original_response,
        "billing/email_broadcast.html",
        email_broadcast_dictionary,
    )


@replace_function("NEMO.views.email.get_users_for_email")
def new_get_users_for_email(old_function, audience: str, selection, no_type: bool) -> (QuerySetType[User], str):
    only_active_projects = no_type
    if audience not in ["group", "pi_institution_types"]:
        return old_function(audience, selection, no_type)
    else:
        try:
            from NEMO_user_details.views.email import new_get_users_for_email as user_details_users_for_email

            if audience == "group":
                return user_details_users_for_email(old_function, audience, selection, no_type)
        except:
            pass
        user_pi_by_institution_type_list = User.objects.none()
        for and_institution_type in selection:
            user_pi_institution_type = User.objects.all()
            for institution_type_pk in and_institution_type.split(" "):
                prj_filter = User.objects.filter(
                    managed_projects__projectbillingdetails__institution__institution_type__in=[
                        int(institution_type_pk)
                    ]
                )
                if only_active_projects:
                    prj_filter = prj_filter.filter(managed_projects__active=True)
                user_pi_institution_type &= prj_filter

            user_pi_by_institution_type_list |= user_pi_institution_type

        return user_pi_by_institution_type_list.distinct(), None


# Let's add custom charges to our billing data
@replace_function("NEMO.views.api.get_billing_charges")
def new_get_billing_charges(old_function, request_params: Dict) -> List[api_billing.BillableItem]:
    billing_form = api_billing.BillingFilterForm(request_params)
    billing_form.is_valid()
    data = old_function(request_params)
    data.extend(get_custom_charges_for_billing(billing_form))
    data.sort(key=lambda x: x.start, reverse=True)
    return data


# And replace it for transfer charges too
@replace_function("NEMO.views.accounts_and_projects.get_billing_charges")
def new_get_billing_charges_transfer(old_function, request_params: Dict) -> List[api_billing.BillableItem]:
    return new_get_billing_charges(request_params)


@replace_function("NEMO.views.accounts_and_projects.do_transfer_charges")
def new_do_transfer_charges(old_function, charges: List[api_billing.BillableItem], new_project_id: int):
    new_project = Project.objects.get(id=new_project_id)
    # check for already invoice items and prevent moving forward if there are any
    # also check if the new project already has an invoice ending later than any charge that would be moved
    invoice_items: List[InvoiceDetailItem] = list(
        InvoiceDetailItem.objects.filter(
            invoice__voided_date__isnull=True, object_id__in=[charge.item.id for charge in charges]
        )
        .select_related("invoice__configuration", "content_type")
        .only("invoice", "content_type", "object_id", "rate", "amount", "discount", "waived")
    )
    already_invoiced_charges = []
    new_project_already_invoiced_charges = []
    for charge in charges:
        matching_items = [
            invoice_item
            for invoice_item in invoice_items
            if invoice_item.object_id == charge.item.id
            and invoice_item.content_type.model == charge.item._meta.model_name
        ]
        if matching_items:
            already_invoiced_charges.append(charge)
        if Invoice.objects.filter(end__gte=charge.end, project_details__project_id=new_project_id).exists():
            new_project_already_invoiced_charges.append(charge)
    if already_invoiced_charges or new_project_already_invoiced_charges:
        errors = []
        if already_invoiced_charges:
            indexes = [f"#{i}" for i, charge in enumerate(charges, start=1) if charge in already_invoiced_charges]
            errors.append(
                f"Charges {', '.join(indexes)} cannot be transferred because they have already been invoiced."
            )
        if new_project_already_invoiced_charges:
            indexes = [
                f"#{i}" for i, charge in enumerate(charges, start=1) if charge in new_project_already_invoiced_charges
            ]
            errors.append(
                f"Charges {', '.join(indexes)} cannot be transferred because project {new_project} has an invoice more recent than these charges."
            )
        raise ValidationError(errors)
    old_function(charges, new_project_id)
    custom_charge_ids = []
    for charge in charges:
        if charge.type == "custom_charge":
            custom_charge_ids.append(charge.item_id)
    CustomCharge.objects.filter(id__in=custom_charge_ids).update(project_id=new_project_id)


def get_custom_charges_for_billing(billing_form: api_billing.BillingFilterForm) -> List[api_billing.BillableItem]:
    queryset = CustomCharge.objects.filter().prefetch_related("project", "project__account", "customer")
    start, end = billing_form.get_start_date(), billing_form.get_end_date()
    queryset = queryset.filter(date__gte=start, date__lte=end)
    if billing_form.get_account_id():
        queryset = queryset.filter(project__account_id=billing_form.get_account_id())
    if billing_form.get_account_name():
        queryset = queryset.filter(project__account__name=billing_form.get_account_name())
    if billing_form.get_project_id():
        queryset = queryset.filter(project__id=billing_form.get_project_id())
    if billing_form.get_project_name():
        queryset = queryset.filter(project__name=billing_form.get_project_name())
    if billing_form.get_application_name():
        queryset = queryset.filter(project__application_identifier=billing_form.get_application_name())
    if billing_form.get_username():
        queryset = queryset.filter(customer__username=billing_form.get_username())
    return billable_items_custom_charges(queryset)


def billable_items_custom_charges(custom_charge_list: QuerySetType[CustomCharge]) -> List[api_billing.BillableItem]:
    billable_items: List[api_billing.BillableItem] = []
    for custom_charge in custom_charge_list:
        try:
            item = api_billing.BillableItem(
                "custom_charge", custom_charge.project, custom_charge.customer, custom_charge
            )
        except:
            # remove when everyone is on NEMO >= 7.2.2
            item = api_billing.BillableItem("custom_charge", custom_charge.project, custom_charge.customer)
        item.name = custom_charge.name
        item.item_id = custom_charge.id
        item.details = f""
        item.start = custom_charge.date
        item.end = custom_charge.date
        item.quantity = Decimal(1)
        item.validated = custom_charge.validated
        item.validated_by = custom_charge.validated_by
        item.waived = custom_charge.waived
        item.waived_on = custom_charge.waived_on
        item.waived_by = custom_charge.waived_by
        billable_items.append(item)
    return billable_items
