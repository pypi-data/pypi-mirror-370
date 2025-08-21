import io
import zipfile
from datetime import datetime
from decimal import Decimal
from logging import getLogger
from typing import List

from NEMO.decorators import accounting_or_manager_required, accounting_or_user_office_or_manager_required, synchronized
from NEMO.models import Account
from NEMO.utilities import (
    BasicDisplayTable,
    date_input_format,
    export_format_datetime,
    format_datetime,
    month_list,
    queryset_search_filter,
)
from NEMO.views.customization import ProjectsAccountsCustomization
from NEMO.views.pagination import SortedPaginator
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Case, F, Func, OuterRef, Prefetch, Subquery, Sum, When
from django.db.models.functions import Coalesce, Length
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET, require_POST

from NEMO_billing.invoices.customization import InvoiceCustomization
from NEMO_billing.invoices.exceptions import (
    InvoiceAlreadyExistException,
    InvoiceGenerationException,
    InvoiceItemsNotInFacilityException,
    NoProjectCategorySetException,
    NoProjectDetailsSetException,
    NoRateSetException,
)
from NEMO_billing.invoices.models import (
    BillableItemType,
    Invoice,
    InvoiceConfiguration,
    InvoicePayment,
    InvoiceSummaryItem,
)
from NEMO_billing.invoices.processors import invoice_data_processor_class as processor
from NEMO_billing.invoices.renderers import CSVInvoiceRenderer
from NEMO_billing.invoices.utilities import category_name_for_item_type, display_amount
from NEMO_billing.models import CoreFacility
from NEMO_billing.rates.models import RateType

invoices_logger = getLogger(__name__)


@accounting_or_user_office_or_manager_required
@require_GET
def invoices(request, year: int = None, month: int = None):
    invoice_list = Invoice.objects.filter(voided_date=None)
    if year:
        invoice_list = invoice_list.filter(start__year=year)
        if month:
            invoice_list = invoice_list.filter(start__month=month)
    # Add outstanding balance (sortable column)
    outstanding_sub = (
        InvoicePayment.objects.filter(invoice=OuterRef("pk"))
        .annotate(total_payments=Coalesce(Func("amount", function="Sum"), Decimal(0)))
        .values("total_payments")
        .order_by()
    )
    invoice_list = invoice_list.annotate(outstanding=F("total_amount") - Subquery(outstanding_sub))

    # Add total tax (sortable column). TODO: might need to change to subquery to avoid issue with duplicates in list of related fields
    invoice_list = invoice_list.annotate(
        total_tax=Sum(
            Case(
                When(
                    invoicesummaryitem__summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.TAX,
                    then=F("invoicesummaryitem__amount"),
                ),
                default=Decimal(0),
            )
        )
    )

    core_facilities = CoreFacility.objects.all()

    for facility in core_facilities:
        sub = InvoiceSummaryItem.objects.filter(
            invoice=OuterRef("pk"),
            core_facility=facility.name,
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.SUBTOTAL,
        ).values("amount")
        invoice_list = invoice_list.annotate(**{f"facility_total_{facility.id}": Subquery(sub)})
    # Add general (None) subtotal too
    sub = InvoiceSummaryItem.objects.filter(
        invoice=OuterRef("pk"), core_facility=None, summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.SUBTOTAL
    ).values("amount")
    invoice_list = invoice_list.annotate(**{f"facility_total_general": Subquery(sub)})

    # Prefetch facility subtotals, projects and configurations
    invoice_list = (
        invoice_list.prefetch_related(
            Prefetch(
                "invoicesummaryitem_set",
                queryset=InvoiceSummaryItem.objects.filter(
                    summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.SUBTOTAL
                ),
                to_attr="facility_subtotals",
            )
        )
        .prefetch_related("project_details__project")
        .prefetch_related("configuration")
    )

    # Fixed sort by number in case they are longer
    paginator = SortedPaginator(invoice_list, request, order_by="-created_date")
    order = request.GET.get("o")
    if order == "-invoice_number":
        paginator.object_list = paginator.object_list.order_by(Length("invoice_number").desc(), "-invoice_number")
    elif order == "invoice_number":
        paginator.object_list = paginator.object_list.order_by(Length("invoice_number").asc(), "invoice_number")

    page = paginator.get_current_page()

    display_general_facility = not core_facilities.exists() or not settings.INVOICE_ALL_ITEMS_MUST_BE_IN_FACILITY

    csv_export = bool(request.GET.get("csv", False))
    if csv_export:
        table_result = BasicDisplayTable()
        table_result.headers = [
            ("number", "Number"),
            ("created", "Created"),
            ("month", "Month"),
            ("project", "Project"),
            ("identifier", ProjectsAccountsCustomization.get("project_application_identifier_name")),
            ("account", "Account"),
            ("sent", "Sent"),
            ("due", "Due"),
            ("reviewed", "Reviewed"),
            ("reviewed_by", "Reviewed by"),
            ("total", "Total"),
        ]
        for core_facility in core_facilities:
            table_result.add_header(("facility_" + core_facility.name, core_facility.name))
        if display_general_facility:
            table_result.add_header(("facility_", "General"))
        table_result.add_header(("tax", "Tax"))
        table_result.add_header(("outstanding", "Outstanding"))
        table_result.add_header(("emails", "Emails"))
        for invoice in page:
            row = {
                "number": invoice.invoice_number,
                "created": format_datetime(invoice.created_date, "SHORT_DATETIME_FORMAT"),
                "month": format_datetime(invoice.start, "F Y"),
                "project": invoice.project_details.name,
                "identifier": invoice.project_details.project.application_identifier,
                "account": invoice.project_details.project.account.name,
                "sent": format_datetime(invoice.last_sent_date, "SHORT_DATE_FORMAT") if invoice.last_sent_date else "",
                "due": format_datetime(invoice.due_date, "SHORT_DATE_FORMAT") if invoice.due_date else "",
                "reviewed": (
                    format_datetime(invoice.reviewed_date, "SHORT_DATE_FORMAT") if invoice.reviewed_date else ""
                ),
                "reviewed_by": invoice.reviewed_by.get_name() if invoice.reviewed_by else "",
                "total": invoice.total_amount_display(),
                "outstanding": display_amount(invoice.outstanding, invoice.configuration),
                "tax": display_amount(invoice.total_tax, invoice.configuration),
                "emails": ",".join(invoice.project_details.email_to()),
            }
            facilities_subtotals = {sub.core_facility: sub for sub in invoice.facility_subtotals}
            for core_facility in core_facilities:
                row["facility_" + core_facility.name] = display_amount(
                    (
                        facilities_subtotals[core_facility.name].amount
                        if core_facility.name in facilities_subtotals
                        else 0
                    ),
                    invoice.configuration,
                )
            if display_general_facility:
                row["facility_"] = display_amount(
                    facilities_subtotals[None].amount if None in facilities_subtotals else 0, invoice.configuration
                )
            table_result.add_row(row)
        response = table_result.to_csv()
        filename = f"invoices_{export_format_datetime()}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    request.session["current_invoice_list_id"] = [invoice.id for invoice in page]

    month_list_since = InvoiceCustomization.get_date("invoice_month_list_since", False) or datetime(
        year=2021, month=1, day=1
    )

    return render(
        request,
        "invoices/invoices.html",
        {
            "page": page,
            "month_list": month_list(since=month_list_since),
            "accounts": Account.objects.all(),
            "configuration_list": InvoiceConfiguration.objects.all(),
            "filter_month_list": Invoice.objects.filter(voided_date=None).dates("start", "month", order="DESC"),
            "filter_year": year or datetime.now().year,
            "filter_month": month,
            "core_facilities": core_facilities,
            "display_general_facility": display_general_facility,
        },
    )


@accounting_or_manager_required
@require_POST
@synchronized()
def generate_monthly_invoices(request):
    extra_tags = "data-speed=20000"
    warning_extra_tags = "data-speed=40000"
    error_extra_tags = "data-speed=40000 data-trigger=manual"
    generated_invoices = []
    has_errors = True
    try:
        account_id: str = request.POST["account_id"]
        configuration_id = request.POST["configuration_id"]
        configuration = get_object_or_404(InvoiceConfiguration, id=configuration_id)
        month = request.POST["month"]
        if account_id == "All":
            for account in Account.objects.all():
                invoice_list = processor.generate_invoice_for_account(month, account, configuration, request.user)
                generated_invoices.extend(invoice_list)
        else:
            account: Account = get_object_or_404(Account, id=account_id)
            invoice_list = processor.generate_invoice_for_account(month, account, configuration, request.user)
            generated_invoices.extend(invoice_list)
        has_errors = False
    except NoProjectDetailsSetException as e:
        link = reverse("project", args=[e.project.id])
        message = "Invoice generation failed: " + e.msg + f" - click <a href='{link}'>here</a> to add some."
        messages.error(request, mark_safe(message), error_extra_tags)
    except NoRateSetException as e:
        link = create_rate_link(e.rate_type, e.tool, e.area, e.consumable)
        message = "Invoice generation failed: " + e.msg + f" - click <a href='{link}'>here</a> to create one."
        messages.error(request, mark_safe(message), error_extra_tags)
    except InvoiceAlreadyExistException as e:
        link = reverse("view_invoice", args=[e.invoice.id])
        message = "Invoice generation failed: " + e.msg + f" - click <a href='{link}'>here</a> to view it."
        messages.error(request, mark_safe(message), error_extra_tags)
    except NoProjectCategorySetException as e:
        link = reverse("project", args=[e.project.id])
        message = "Invoice generation failed: " + e.msg + f" - click <a href='{link}'>here</a> to set it."
        messages.error(request, mark_safe(message), error_extra_tags)
    except InvoiceItemsNotInFacilityException as e:
        messages.error(request, e.msg, error_extra_tags)
    except InvoiceGenerationException as e:
        link = reverse("re_render_invoice", args=[e.invoice.id])
        message = e.msg + f" - click <a href='{link}'>here</a> to try generating it again."
        messages.error(request, mark_safe(message), error_extra_tags)
    except Exception as e:
        invoices_logger.exception(e)
        messages.error(request, str(e), error_extra_tags)
    if generated_invoices:
        messages.success(request, f"{len(generated_invoices)} invoice(s) were generated successfully.", extra_tags)
    else:
        messages.warning(
            request,
            f"No invoices were generated. {'Either the invoices already exist or there was no usage for that month' if not has_errors else ' Please correct the issues and try again.'}",
            warning_extra_tags,
        )
    return redirect("invoices")


@accounting_or_user_office_or_manager_required
@require_GET
def search_invoices(request):
    return queryset_search_filter(
        Invoice.objects.all(),
        ["invoice_number", "project_details__project__name", "project_details__project__account__name"],
        request,
    )


@accounting_or_user_office_or_manager_required
@require_GET
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    dictionary = {
        "invoice": invoice,
        "core_facilities": CoreFacility.objects.exists(),
        "tool_title": category_name_for_item_type(BillableItemType.TOOL_USAGE),
        "area_title": category_name_for_item_type(BillableItemType.AREA_ACCESS),
        "staff_charge_title": category_name_for_item_type(BillableItemType.STAFF_CHARGE),
        "consumable_title": category_name_for_item_type(BillableItemType.CONSUMABLE),
        "training_title": category_name_for_item_type(BillableItemType.TRAINING),
        "missed_reservation_title": category_name_for_item_type(BillableItemType.MISSED_RESERVATION),
        "custom_charge_title": category_name_for_item_type(BillableItemType.CUSTOM_CHARGE),
    }
    invoice_list_ids = (
        request.session["current_invoice_list_id"] if "current_invoice_list_id" in request.session else []
    )
    if invoice.id in invoice_list_ids:
        index = invoice_list_ids.index(invoice.id)
        dictionary.update(
            {
                "previous_id": invoice_list_ids[index - 1] if index - 1 >= 0 else None,
                "next_id": invoice_list_ids[index + 1] if index + 1 < len(invoice_list_ids) else None,
            }
        )

    return render(request, "invoices/invoice.html", dictionary)


def create_rate_link(rate_type, tool, area, consumable):
    try:
        if rate_type and rate_type.type == RateType.Type.CONSUMABLE:
            return reverse("create_rate", args=[RateType.Type.CONSUMABLE, consumable.id])
        elif rate_type and rate_type.get_rate_group_type() == RateType.Type.TOOL:
            return reverse("create_rate", args=[RateType.Type.TOOL, tool.id])
        elif rate_type and rate_type.get_rate_group_type() == RateType.Type.AREA:
            return reverse("create_rate", args=[RateType.Type.AREA, area.id])
        elif rate_type:
            reverse("create_rate", args=[rate_type.type])
    except:
        pass
    return reverse("create_rate")


@accounting_or_manager_required
@require_POST
def review_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if not invoice.reviewed_date:
        invoice.reviewed_date = timezone.now()
        invoice.reviewed_by = request.user
        invoice.save()
        messages.success(request, f"Invoice {invoice.invoice_number} was successfully marked as reviewed.")
    else:
        messages.error(request, f"Invoice {invoice.invoice_number} has already been reviewed.")
    return redirect("view_invoice", invoice_id=invoice_id)


@accounting_or_manager_required
@require_POST
def send_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if invoice.reviewed_date:
        if not invoice.project_details.email_to():
            link = reverse("project", args=[invoice.project_details.project.id])
            messages.error(
                request,
                mark_safe(
                    f"Invoice {invoice.invoice_number} could not sent because no email is set on the project - click <a href='{link}'>here</a> to add some"
                ),
            )
        else:
            sent = invoice.send()
            if sent:
                messages.success(request, f"Invoice {invoice.invoice_number} was successfully sent.")
            else:
                messages.error(request, f"Invoice {invoice.invoice_number} could not be sent.")
    else:
        messages.error(request, f"Invoice {invoice.invoice_number} needs to be reviewed before sending.")
    return redirect("view_invoice", invoice_id=invoice_id)


@accounting_or_manager_required
@require_POST
def void_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    processor.void_invoice(invoice, request)
    return redirect("view_invoice", invoice_id=invoice_id)


@accounting_or_manager_required
@require_POST
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    processor.delete_invoice(invoice, request)
    return redirect("invoices")


@accounting_or_user_office_or_manager_required
@require_POST
def zip_invoices(request, file_type="file"):
    invoice_ids: List[str] = request.POST.getlist("selected_invoice_id[]")
    if not invoice_ids:
        return redirect("invoices")
    else:
        return zip_response(request, Invoice.objects.filter(id__in=invoice_ids), file_type)


@accounting_or_user_office_or_manager_required
@require_POST
def review_and_send_invoices(request):
    invoice_ids: List[str] = request.POST.getlist("selected_invoice_id[]")
    for invoice_id in invoice_ids:
        review_invoice(request, invoice_id)
        send_invoice(request, invoice_id)
    return redirect("invoices")


@accounting_or_user_office_or_manager_required
@require_POST
def mark_invoices_paid_in_full(request):
    invoice_ids: List[str] = request.POST.getlist("selected_invoice_id[]")
    for invoice_id in invoice_ids:
        mark_invoice_paid_in_full(request, invoice_id)
    return redirect("invoices")


@accounting_or_user_office_or_manager_required
@require_GET
def mark_invoice_paid_in_full(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    invoice.mark_as_paid_in_full(request.user)
    return redirect("view_invoice", invoice_id=invoice_id)


@accounting_or_user_office_or_manager_required
@require_GET
def re_render_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    try:
        if invoice.file:
            messages.warning(request, "This invoice already has a rendered invoice on file")
        else:
            invoice.render_and_save_file()
            messages.success(request, "Invoice generated successfully")
    except InvoiceGenerationException as e:
        extra_tags = "data-speed=30000"
        link = reverse("re_render_invoice", args=[e.invoice.id])
        message = e.msg + f" - click <a href='{link}'>here</a> to try generating it again."
        messages.error(request, mark_safe(message), extra_tags)
    return redirect(request.META.get("HTTP_REFERER", "invoices"))


@accounting_or_user_office_or_manager_required
@require_GET
def csv_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    try:
        invoice_renderer = CSVInvoiceRenderer()
        content = invoice_renderer.render_invoice(invoice)
        content.seek(0)
        response = HttpResponse(content.read(), content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{invoice.filename(invoice_renderer.get_file_extension())}"'
        )
        return response
    except InvoiceGenerationException as e:
        messages.error(request, e.msg)
        return HttpResponse()


@accounting_or_manager_required
@require_POST
def invoice_payment_received(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    amount = Decimal(request.POST["payment_received_amount"])
    note = request.POST.get("payment_note")
    received = datetime.strptime(request.POST["payment_received_date"], date_input_format)
    payment = invoice.record_payment(request.user, amount, received, note=note)
    messages.success(
        request,
        f"The payment of {payment.amount_display()} for invoice {invoice.invoice_number} was marked as received on {date_format(payment.payment_received)}.",
    )
    return redirect("view_invoice", invoice_id=invoice_id)


@accounting_or_manager_required
@require_POST
def invoice_payment_processed(request, payment_id):
    payment = get_object_or_404(InvoicePayment, id=payment_id)
    payment.updated_by = request.user
    payment.payment_processed = datetime.strptime(request.POST["payment_processed_date"], date_input_format)
    payment.save()
    messages.success(
        request,
        f"The payment of {payment.amount_display()} for invoice {payment.invoice.invoice_number} was marked as processed on {date_format(payment.payment_processed)}.",
    )
    return redirect("view_invoice", invoice_id=payment.invoice_id)


@login_required
@require_GET
@permission_required("NEMO.trigger_timed_services", raise_exception=True)
def send_invoice_payment_reminder(request):
    return do_send_invoice_payment_reminder()


def do_send_invoice_payment_reminder():
    today = timezone.now()
    unpaid_invoices = Invoice.objects.filter(due_date__lte=today, voided_date=None)
    for unpaid_invoice in unpaid_invoices:
        if unpaid_invoice.total_outstanding_amount() > Decimal(0):
            if not unpaid_invoice.last_reminder_sent_date:
                unpaid_invoice.send_reminder()
            else:
                # Check days since last reminder sent
                time_diff = today - unpaid_invoice.last_reminder_sent_date
                too_long_since_last = (
                    unpaid_invoice.configuration.reminder_frequency
                    and time_diff.days >= unpaid_invoice.configuration.reminder_frequency
                )
                # Send reminder if none has been sent yet, or if it's been too long
                if too_long_since_last:
                    unpaid_invoice.send_reminder()
    return HttpResponse()


def zip_response(request, invoice_list: List[Invoice], file_type="file"):
    generated_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    parent_folder_name = f"invoices_{generated_date}"
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode="w", compression=zipfile.ZIP_DEFLATED) as backup_zip:
        csv_invoice_renderer = CSVInvoiceRenderer()
        for invoice in invoice_list:
            if file_type.lower() == "csv":
                ext = csv_invoice_renderer.get_file_extension()
                content = csv_invoice_renderer.render_invoice(invoice)
                content.seek(0)
                backup_zip.writestr(f"{parent_folder_name}/" + invoice.filename_for_zip(ext), content.read())
                content.close()
            elif invoice.file:
                backup_zip.write(invoice.file.path, f"{parent_folder_name}/" + invoice.filename_for_zip())
    response = HttpResponse(zip_io.getvalue(), content_type="application/x-zip-compressed")
    response["Content-Disposition"] = "attachment; filename=%s" % parent_folder_name + ".zip"
    response["Content-Length"] = zip_io.tell()
    return response
