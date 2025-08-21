import importlib
from abc import ABC, abstractmethod
from decimal import Decimal
from io import BytesIO, IOBase
from typing import Any, List, Tuple

from NEMO.utilities import BasicDisplayTable
from NEMO.views.customization import ApplicationCustomization, ProjectsAccountsCustomization
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

from NEMO_billing.invoices.exceptions import (
    InvoiceGenerationException,
)
from NEMO_billing.invoices.models import (
    BillableItemType,
    Invoice,
    InvoiceDetailItem,
    InvoiceSummaryItem,
)
from NEMO_billing.invoices.utilities import category_name_for_item_type, display_amount
from NEMO_billing.pdf_utilities import (
    HEADING_FONT,
    HEADING_FONT_CENTERED,
    PDFDocument,
    PDFPageSize,
    SMALL_FONT,
    SMALL_FONT_RIGHT,
)


class InvoiceRenderer(ABC):
    def __init__(self):
        self.date_time_format = settings.INVOICE_DATETIME_FORMAT
        self.date_format = settings.INVOICE_DATE_FORMAT

    def render_invoice(self, invoice: Invoice) -> IOBase:
        try:
            file_bytes = BytesIO()
            document = self.init_document(invoice, file_bytes)
            self.render_front_page(invoice, document)
            self.render_summary(invoice, document)
            if invoice.configuration.detailed_invoice:
                self.render_details(invoice, document)
            return self.close_document(invoice, document, file_bytes)
        except Exception as e:
            raise InvoiceGenerationException(invoice, self, e)

    @abstractmethod
    def get_file_extension(self):
        pass

    @abstractmethod
    def init_document(self, invoice: Invoice, file_bytes: IOBase) -> Any:
        pass

    @abstractmethod
    def render_front_page(self, invoice: Invoice, document):
        pass

    @abstractmethod
    def render_summary(self, invoice: Invoice, document):
        pass

    @abstractmethod
    def render_details(self, invoice: Invoice, document):
        pass

    def close_document(self, invoice: Invoice, document, file_bytes: IOBase) -> IOBase:
        return file_bytes

    def format_date_time(self, datetime, date_only: bool = False):
        tz_datetime = datetime.astimezone(timezone.get_current_timezone())
        return tz_datetime.strftime(self.date_format) if date_only else tz_datetime.strftime(self.date_time_format)


class PDFInvoiceRenderer(InvoiceRenderer):
    def get_file_extension(self):
        return "pdf"

    def init_document(self, invoice: Invoice, file_bytes) -> PDFDocument:
        pdf = PDFDocument(
            buffer_bytes=file_bytes,
            pagesize=PDFPageSize.Letter,
            header_text=invoice.configuration.merchant_details,
            header_logo=invoice.configuration.merchant_logo,
            document_author=invoice.created_by.get_name(),
            document_title=f"{invoice.configuration.invoice_title} {invoice.invoice_number}",
        )
        return pdf

    def render_front_page(self, invoice: Invoice, pdf: PDFDocument):
        default_style = pdf.styles[f"{SMALL_FONT}Base11"]
        default_italic_style = pdf.styles[f"{SMALL_FONT}Italic10"]
        heading_style = pdf.styles[f"{HEADING_FONT}Bold18"]
        heading_style_centered = pdf.styles[f"{HEADING_FONT_CENTERED}Bold18"]
        details_key_style = pdf.styles[f"{SMALL_FONT}Bold12"]
        total_charges_style = pdf.styles[f"{SMALL_FONT}Base12"]
        pdf.add_space(1, 10)
        pdf.add_title(invoice.configuration.invoice_title)
        key_value_col_width = [65, None]
        pdf.add_space(1, 30)
        details_data = [
            ("Date:", self.format_date_time(invoice.created_date, date_only=True)),
            ("Number:", invoice.invoice_number),
            ("Project:", invoice.project_details.name),
            (
                ProjectsAccountsCustomization.get("project_application_identifier_name") + ":",
                invoice.project_details.project.application_identifier,
            ),
        ]
        pdf.add_table_key_value(details_data, key_value_col_width, details_key_style, default_style)
        pdf.add_space(1, 15)
        if invoice.project_details.addressee:
            pdf.add_table_key_value(
                [("To:", invoice.project_details.addressee)], key_value_col_width, details_key_style, default_style
            )
        pdf.add_space(1, 50)
        facility = ApplicationCustomization.get("facility_name")
        pdf.add_heading_paragraph(
            f"{facility} charges for {invoice.start.strftime(self.date_format)} to {invoice.end.strftime(self.date_format)}",
            heading_style_centered,
            fit=True,
            border=True,
        )
        pdf.add_space(1, 15)
        pdf.add_paragraph(
            f"Total {facility} charges: <b>{invoice.total_amount_display()}</b>", style=total_charges_style
        )
        pdf.add_space(1, 5)
        pdf.add_paragraph(f"Please refer to attached summary for details.", default_italic_style)
        if invoice.configuration.terms:
            pdf.add_space(1, 70)
            pdf.add_heading_paragraph("Terms and Conditions:", heading_style)
            pdf.add_paragraph(invoice.configuration.terms, default_style)

    def render_summary(self, invoice: Invoice, pdf: PDFDocument):
        header_name_style = pdf.styles[f"{SMALL_FONT}Bold10"]
        header_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold10"]
        category_name_style = pdf.styles[f"{SMALL_FONT}Bold12"]
        category_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base12"]
        item_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base10"]
        other_name_style = pdf.styles[f"{SMALL_FONT}Bold10"]
        total_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold12"]
        pdf.add_page_break()
        pdf.add_title("Summary")
        table_data = []
        # Separate type based on invoice configuration options
        separate_item_types: List[BillableItemType] = []
        facility_item_types: List[BillableItemType] = []

        if invoice.configuration.separate_tool_usage_charges:
            separate_item_types.append(BillableItemType.TOOL_USAGE)
        else:
            facility_item_types.append(BillableItemType.TOOL_USAGE)
        if invoice.configuration.separate_area_access_charges:
            separate_item_types.append(BillableItemType.AREA_ACCESS)
        else:
            facility_item_types.append(BillableItemType.AREA_ACCESS)
        if invoice.configuration.separate_consumable_charges:
            separate_item_types.append(BillableItemType.CONSUMABLE)
        else:
            facility_item_types.append(BillableItemType.CONSUMABLE)
        if invoice.configuration.separate_missed_reservation_charges:
            separate_item_types.append(BillableItemType.MISSED_RESERVATION)
        else:
            facility_item_types.append(BillableItemType.MISSED_RESERVATION)
        if invoice.configuration.separate_staff_charges:
            separate_item_types.append(BillableItemType.STAFF_CHARGE)
        else:
            facility_item_types.append(BillableItemType.STAFF_CHARGE)
        if invoice.configuration.separate_training_charges:
            separate_item_types.append(BillableItemType.TRAINING)
        else:
            facility_item_types.append(BillableItemType.TRAINING)
        if invoice.configuration.separate_custom_charges:
            separate_item_types.append(BillableItemType.CUSTOM_CHARGE)
        else:
            facility_item_types.append(BillableItemType.CUSTOM_CHARGE)

        # Deal first with non-empty core facilities
        for core_facility in invoice.sorted_core_facilities():
            if core_facility:
                facility_summaries = invoice.invoicesummaryitem_set.filter(core_facility=core_facility)
                summary_items = facility_summaries.filter(
                    summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.ITEM
                )
                facility_display_items = summary_items.filter(item_type__in=[t.value for t in facility_item_types])
                sub_total_amount = facility_display_items.aggregate(Sum("amount"))["amount__sum"]
                # Don't show the facility if there are no items in it
                if facility_display_items.exists():
                    table_data.append(["", "", ""])
                    table_data.append(
                        [(core_facility, category_name_style), ("", category_name_style), ("", category_amount_style)]
                    )
                    for item_type in facility_item_types:
                        items = summary_items.filter(item_type=item_type.value)
                        self.add_items(invoice.configuration, table_data, items, pdf)
                    discounts_amount = self.add_discounts(invoice.configuration, table_data, facility_summaries, pdf)
                    table_data.append(
                        [
                            ("Subtotal", other_name_style),
                            "",
                            (
                                display_amount(sub_total_amount + discounts_amount, invoice.configuration),
                                item_amount_style,
                            ),
                        ]
                    )

        # Add items not in any facilities (and items set as separate in configuration)
        general_summaries = invoice.invoicesummaryitem_set.filter(core_facility=None)
        general_summary_items = general_summaries.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.ITEM
        )
        for item_type in facility_item_types + separate_item_types:
            if item_type in facility_item_types:
                items = general_summary_items.filter(item_type=item_type.value)
            else:
                items = invoice.invoicesummaryitem_set.filter(item_type=item_type.value)
            if items.exists():
                table_data.append(["", "", ""])
                table_data.append(
                    [(category_name_for_item_type(item_type), category_name_style), "", ("", category_amount_style)]
                )
                self.add_items(invoice.configuration, table_data, items, pdf)
                sub_total_amount = items.aggregate(Sum("amount"))["amount__sum"]
                discounts_amount = self.add_discounts(invoice.configuration, table_data, general_summaries, pdf)
                table_data.append(
                    [
                        ("Subtotal", other_name_style),
                        "",
                        (display_amount(sub_total_amount + discounts_amount, invoice.configuration), item_amount_style),
                    ]
                )

        total_charges_amount = invoice.invoicesummaryitem_set.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.SUBTOTAL
        ).aggregate(Sum("amount"))["amount__sum"]
        table_data.append(["", "", ""])
        table_data.append(
            [
                ("Total Charges", category_name_style),
                "",
                (display_amount(total_charges_amount, invoice.configuration), category_amount_style),
            ]
        )

        tax_item = invoice.invoicesummaryitem_set.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.TAX
        ).first()
        if tax_item:
            table_data.append(
                [
                    (tax_item.name, category_name_style),
                    tax_item.details or "",
                    (display_amount(tax_item.amount, invoice.configuration), category_amount_style),
                ]
            )

        fund_items = invoice.invoicesummaryitem_set.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.FUND
        )
        for fund_summary in fund_items:
            table_data.append(
                [
                    (fund_summary.name, category_name_style),
                    "",  # Don't show details for Fund (it contains the id)
                    (display_amount(fund_summary.amount, invoice.configuration), category_amount_style),
                ]
            )

        other_items = invoice.invoicesummaryitem_set.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.OTHER
        )
        for other_summary in other_items:
            table_data.append(
                [
                    (other_summary.name, other_name_style),
                    "",  # Don't show details for Fund (it contains the id)
                    (display_amount(other_summary.amount, invoice.configuration), category_amount_style),
                ]
            )

        table_data.append(
            [
                ("Grand Total", category_name_style),
                "",
                (display_amount(invoice.total_amount, invoice.configuration), total_amount_style),
            ]
        )
        summary_col_width = [None, 87, 87]
        pdf.add_table(
            table_data,
            headers=[("Item", header_name_style), ("Rate", header_name_style), ("Amount Due", header_amount_style)],
            col_width=summary_col_width,
            grid=False,
            border=True,
        )

    def add_discounts(self, configuration, table_data, summaries_qs, pdf) -> Decimal:
        discount_name_style = pdf.styles[f"{SMALL_FONT}Bold9"]
        discounts_qs = summaries_qs.filter(summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.DISCOUNT)
        item_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base10"]
        total_discounts_amount = Decimal(0)
        for facility_discount in discounts_qs:
            facility_discount_amount = facility_discount.amount
            table_data.append(
                [
                    (facility_discount.name, discount_name_style),
                    (facility_discount.details or ""),
                    (display_amount(facility_discount_amount, configuration), item_amount_style),
                ]
            )
            total_discounts_amount += facility_discount_amount
        return total_discounts_amount

    def add_items(self, configuration, table_data, summary_items_qs, pdf):
        item_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base10"]
        for item in summary_items_qs:
            if not configuration.hide_zero_charge or item.amount != Decimal(0):
                # Add prefix of category name only if we have a facility (otherwise it will be in the category with that name)
                item_name = (
                    f"{category_name_for_item_type(item.item_type)} - {item.name}"
                    if item.core_facility
                    else f"{item.name}"
                )
                table_data.append(
                    [item_name, item.details or "", (display_amount(item.amount, configuration), item_amount_style)]
                )

    def render_details(self, invoice: Invoice, pdf: PDFDocument):
        default_style = pdf.styles[f"{SMALL_FONT}Base12"]
        heading_style_centered = pdf.styles[f"{HEADING_FONT_CENTERED}Bold18"]
        pdf.add_page_break()
        seven_col_width = [None, None, None, None, 65, 77, 50]
        six_col_width = [None, None, None, 65, 77, 50]
        four_col_width = [None, None, None, 50]
        for core_facility in invoice.sorted_core_facilities():
            facility_name = core_facility or "General Charges"
            pdf.add_space(1, 20)
            pdf.add_heading_paragraph(facility_name, heading_style_centered, border=True)
            pdf.add_space(1, 20)
            tool_details = invoice.tool_usage_details(core_facility=core_facility)
            if tool_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph(category_name_for_item_type(BillableItemType.TOOL_USAGE), default_style)
                pdf.add_table(
                    *self.duration_details_data(tool_details, "Tool", pdf), col_width=seven_col_width, grid=False
                )
            area_details = invoice.area_access_details(core_facility=core_facility)
            if area_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph(category_name_for_item_type(BillableItemType.AREA_ACCESS), default_style)
                pdf.add_table(
                    *self.duration_details_data(area_details, "Area", pdf), col_width=seven_col_width, grid=False
                )
            staff_charges_details = invoice.staff_charge_details(core_facility=core_facility)
            if staff_charges_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph(category_name_for_item_type(BillableItemType.STAFF_CHARGE), default_style)
                pdf.add_table(
                    *self.duration_details_data(staff_charges_details, "Item", pdf),
                    col_width=seven_col_width,
                    grid=False,
                )
            consumable_withdrawals = invoice.consumable_withdrawal_details(core_facility=core_facility)
            if consumable_withdrawals.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph(category_name_for_item_type(BillableItemType.CONSUMABLE), default_style)
                pdf.add_table(
                    *self.consumable_details_data(consumable_withdrawals, pdf), col_width=six_col_width, grid=False
                )
            training_details = invoice.training_details(core_facility=core_facility)
            if training_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph(category_name_for_item_type(BillableItemType.TRAINING), default_style)
                pdf.add_table(*self.training_details_data(training_details, pdf), col_width=six_col_width, grid=False)
            missed_details = invoice.missed_reservation_details(core_facility=core_facility)
            if missed_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph(category_name_for_item_type(BillableItemType.MISSED_RESERVATION), default_style)
                pdf.add_table(
                    *self.duration_details_data(missed_details, "Reservation", pdf),
                    col_width=seven_col_width,
                    grid=False,
                )
            custom_details = invoice.custom_charges_details(core_facility=core_facility)
            if custom_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph(category_name_for_item_type(BillableItemType.CUSTOM_CHARGE), default_style)
                pdf.add_table(
                    *self.custom_charge_details_data(custom_details, pdf), col_width=four_col_width, grid=False
                )

    def close_document(self, invoice: Invoice, pdf: PDFDocument, file_bytes: IOBase) -> IOBase:
        pdf.build()
        return super().close_document(invoice, pdf, file_bytes)

    def duration_details_data(self, items: List[InvoiceDetailItem], item_name: str, pdf) -> Tuple[List[List], List]:
        last_item_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base8"]
        last_header_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold10"]
        return (
            [
                [
                    str(item.user),
                    item.name,
                    self.format_date_time(item.start),
                    self.format_date_time(item.end),
                    item.quantity_display(),
                    item.rate,
                    (item.amount_display(), last_item_style),
                ]
                for item in items
            ],
            ["User", item_name, "Start Time", "End Time", "Quantity", "Rate", ("Amount", last_header_style)],
        )

    def consumable_details_data(self, items: List[InvoiceDetailItem], pdf) -> Tuple[List[List], List]:
        last_item_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base8"]
        last_header_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold10"]
        return (
            [
                [
                    str(item.user),
                    item.name,
                    self.format_date_time(item.start),
                    item.quantity_display(),
                    item.rate,
                    (item.amount_display(), last_item_style),
                ]
                for item in items
            ],
            ["User", "Supply", "Date", "Quantity", "Rate", ("Amount", last_header_style)],
        )

    def training_details_data(self, items: List[InvoiceDetailItem], pdf) -> Tuple[List[List], List]:
        last_item_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base8"]
        last_header_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold10"]
        return (
            [
                [
                    str(item.user),
                    "Tool",
                    self.format_date_time(item.start),
                    item.quantity_display(),
                    item.rate,
                    (item.amount_display(), last_item_style),
                ]
                for item in items
            ],
            ["User", "Tool", "Date", "Duration", "Rate", ("Amount", last_header_style)],
        )

    def custom_charge_details_data(self, items: List[InvoiceDetailItem], pdf) -> Tuple[List[List], List]:
        last_item_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base8"]
        last_header_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold10"]
        return (
            [
                [str(item.user), item.name, self.format_date_time(item.start), (item.amount_display(), last_item_style)]
                for item in items
            ],
            ["User", "Charge", "Date", ("Amount", last_header_style)],
        )


class CSVInvoiceRenderer(InvoiceRenderer):
    PROJECT_ID_KEY = "application_identifier"
    ACCOUNT_TYPE_KEY = "account_type"
    FACILITY_KEY = "facility"
    USER_KEY = "user"
    ITEM_TYPE_KEY = "item_type"
    ITEM_KEY = "item"
    START_KEY = "start"
    END_KEY = "end"
    QUANTITY_KEY = "quantity"
    RATE_KEY = "rate"
    DISCOUNT_KEY = "discount"
    AMOUNT_KEY = "amount"

    def __init__(self):
        super().__init__()

    def get_file_extension(self):
        return "csv"

    def init_document(self, invoice: Invoice, file_bytes) -> Any:
        document = BasicDisplayTable()
        document.add_header(
            (self.PROJECT_ID_KEY, ProjectsAccountsCustomization.get("project_application_identifier_name"))
        )
        if invoice.project_details.project.account.type:
            document.add_header((self.ACCOUNT_TYPE_KEY, "Account type"))
        if invoice.invoicedetailitem_set.filter(core_facility__isempty=False).exists():
            document.add_header((self.FACILITY_KEY, "Facility"))
        document.add_header((self.USER_KEY, "User"))
        document.add_header((self.ITEM_TYPE_KEY, "Item Type"))
        document.add_header((self.ITEM_KEY, "Item"))
        document.add_header((self.START_KEY, "Start Time"))
        document.add_header((self.END_KEY, "End Time"))
        document.add_header((self.QUANTITY_KEY, "Quantity"))
        document.add_header((self.RATE_KEY, "Rate"))
        document.add_header((self.DISCOUNT_KEY, "Discount"))
        document.add_header((self.AMOUNT_KEY, "Amount"))
        return document

    def render_front_page(self, invoice: Invoice, document):
        pass

    def render_summary(self, invoice: Invoice, document):
        pass

    def render_details(self, invoice: Invoice, document: BasicDisplayTable):
        for item in invoice.invoice_details().order_by("-start"):
            document.add_row(
                {
                    self.PROJECT_ID_KEY: invoice.project_details.project.application_identifier,
                    self.ACCOUNT_TYPE_KEY: invoice.project_details.project.account.type,
                    self.FACILITY_KEY: item.core_facility,
                    self.USER_KEY: item.user,
                    self.ITEM_TYPE_KEY: item.get_item_type_display(),
                    self.ITEM_KEY: item.name,
                    self.START_KEY: self.format_date_time(item.start),
                    self.END_KEY: self.format_date_time(item.end),
                    self.QUANTITY_KEY: item.quantity,
                    self.RATE_KEY: item.rate,
                    self.DISCOUNT_KEY: "waived" if item.waived else item.discount,
                    self.AMOUNT_KEY: item.amount,
                }
            )
        for discount in invoice.invoicesummaryitem_set.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.DISCOUNT
        ):
            document.add_row(
                {
                    self.PROJECT_ID_KEY: invoice.project_details.project.application_identifier,
                    self.ACCOUNT_TYPE_KEY: invoice.project_details.project.account.type,
                    self.FACILITY_KEY: discount.core_facility,
                    self.ITEM_TYPE_KEY: discount.get_item_type_display(),
                    self.ITEM_KEY: discount.name,
                    self.AMOUNT_KEY: discount.amount,
                }
            )
        for other in invoice.invoicesummaryitem_set.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.OTHER
        ):
            document.add_row(
                {
                    self.PROJECT_ID_KEY: invoice.project_details.project.application_identifier,
                    self.ACCOUNT_TYPE_KEY: invoice.project_details.project.account.type,
                    self.FACILITY_KEY: other.core_facility,
                    self.ITEM_TYPE_KEY: other.get_item_type_display(),
                    self.ITEM_KEY: other.name,
                    self.AMOUNT_KEY: other.amount,
                }
            )
        for tax in invoice.invoicesummaryitem_set.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.TAX
        ):
            document.add_row(
                {
                    self.FACILITY_KEY: tax.core_facility,
                    self.ITEM_TYPE_KEY: tax.get_item_type_display(),
                    self.ITEM_KEY: tax.name,
                    self.AMOUNT_KEY: tax.amount,
                }
            )
        for fund in invoice.invoicesummaryitem_set.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.FUND
        ):
            document.add_row(
                {
                    self.ITEM_TYPE_KEY: fund.get_item_type_display(),
                    self.ITEM_KEY: fund.name,
                    self.AMOUNT_KEY: fund.amount,
                }
            )
        document.add_row({self.DISCOUNT_KEY: "Total", self.AMOUNT_KEY: invoice.total_amount})

    def close_document(self, invoice: Invoice, document: BasicDisplayTable, file_bytes: IOBase):
        # write the bytes and let the parent class return it
        file_bytes = BytesIO(document.to_csv().content)
        return super().close_document(invoice, document, file_bytes)


def get_invoice_renderer_class() -> InvoiceRenderer:
    renderer_class = getattr(settings, "INVOICE_RENDERER_CLASS", "NEMO_billing.invoices.renderers.PDFInvoiceRenderer")
    assert isinstance(renderer_class, str)
    pkg, attr = renderer_class.rsplit(".", 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret()


invoice_renderer_class = get_invoice_renderer_class()
