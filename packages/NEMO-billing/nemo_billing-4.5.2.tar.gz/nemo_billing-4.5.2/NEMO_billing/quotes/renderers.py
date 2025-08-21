import importlib
from abc import ABC, abstractmethod
from io import IOBase
from typing import Any

from django.conf import settings
from django.utils import timezone
from six import BytesIO

from NEMO_billing.pdf_utilities import HEADING_FONT, PDFDocument, PDFPageSize, SMALL_FONT, SMALL_FONT_RIGHT
from NEMO_billing.quotes.exceptions import QuoteGenerationException
from NEMO_billing.quotes.models import Quote


class QuoteRenderer(ABC):
    def __init__(self):
        self.date_time_format = settings.QUOTE_DATETIME_FORMAT
        self.date_format = settings.QUOTE_DATE_FORMAT

    def render(self, quote: Quote) -> IOBase:
        try:
            file_bytes = BytesIO()
            document = self.init_document(quote, file_bytes)
            self.render_prelude(quote, document)
            self.render_quote_table(quote, document)
            return self.close_document(quote, document, file_bytes)
        except Exception as e:
            raise QuoteGenerationException(quote, self, e)

    @abstractmethod
    def get_file_extension(self):
        pass

    @abstractmethod
    def init_document(self, quote: Quote, file_bytes: IOBase) -> Any:
        pass

    @abstractmethod
    def render_prelude(self, quote: Quote, document):
        pass

    @abstractmethod
    def render_quote_table(self, quote: Quote, document):
        pass

    def close_document(self, quote: Quote, document, file_bytes: IOBase) -> IOBase:
        return file_bytes

    def format_date_time(self, datetime, date_only: bool = False):
        tz_datetime = datetime.astimezone(timezone.get_current_timezone())
        return tz_datetime.strftime(self.date_format) if date_only else tz_datetime.strftime(self.date_time_format)


class PDFQuoteRenderer(QuoteRenderer):

    def get_file_extension(self):
        return "pdf"

    def init_document(self, quote: Quote, file_bytes):
        pdf = PDFDocument(
            buffer_bytes=file_bytes,
            pagesize=PDFPageSize.Letter,
            header_text=quote.configuration.merchant_details,
            header_logo=quote.configuration.merchant_logo,
            document_author=quote.creator.get_name(),
            document_title=quote.name,
        )
        return pdf

    def render_prelude(self, quote: Quote, pdf: PDFDocument):
        default_style = pdf.styles[f"{SMALL_FONT}Base11"]
        heading_style = pdf.styles[f"{HEADING_FONT}Bold18"]
        details_key_style = pdf.styles[f"{SMALL_FONT}Bold12"]
        pdf.add_space(1, 10)
        pdf.add_title(quote.name)
        key_value_col_width = [None, None]
        pdf.add_space(1, 30)
        details_data = [
            ("Date:", self.format_date_time(quote.published_date, date_only=True)),
        ]
        if quote.quote_number:
            details_data.append(("Quote Number:", quote.quote_number))
        if quote.project:
            details_data.append(("Project:", quote.project.name))
        if quote.expiration_date:
            details_data.append(("Expires on:", quote.expiration_date.strftime(self.date_format)))
        details_data.append(("Total:", quote.total_display))
        pdf.add_table_key_value(details_data, key_value_col_width, details_key_style, default_style)
        if quote.configuration.terms:
            pdf.add_space(1, 70)
            pdf.add_heading_paragraph("Terms and Conditions:", heading_style)
            pdf.add_paragraph(quote.configuration.terms, default_style)

    def render_quote_table(self, quote: Quote, pdf: PDFDocument):
        header_name_style = pdf.styles[f"{SMALL_FONT}Bold10"]
        header_total_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold10"]
        item_text_style = pdf.styles[f"{SMALL_FONT}Base10"]
        item_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base10"]
        total_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold12"]
        total_text_style = pdf.styles[f"{SMALL_FONT}Bold12"]

        pdf.add_space(1, 30)
        table_data = []

        for item in quote.items:
            table_data.append(
                [
                    (item.description, item_text_style),
                    (f"{item.quantity}", item_text_style),
                    (item.display_rate, item_text_style),
                    (item.total_display, item_amount_style),
                ]
            )

        if quote.configuration.tax and quote.add_tax:
            table_data.append(
                [
                    (f"Tax ({quote.configuration.tax_name})", item_text_style),
                    "",
                    (quote.tax_display, item_text_style),
                    (quote.tax_amount_display, item_amount_style),
                ]
            )

        table_data.append(
            [
                ("Total", total_text_style),
                "",
                "",
                (quote.total_display, total_amount_style),
            ]
        )
        summary_col_width = [None, 80, 80, None]
        pdf.add_table(
            table_data,
            headers=[
                ("Item", header_name_style),
                ("Quantity", header_name_style),
                ("Rate", header_name_style),
                ("Total", header_total_style),
            ],
            col_width=summary_col_width,
            grid=False,
            border=True,
        )

    def close_document(self, quote: Quote, pdf: PDFDocument, file_bytes: IOBase) -> IOBase:
        pdf.build()
        return file_bytes


def get_quote_renderer_class() -> QuoteRenderer:
    renderer_class = getattr(settings, "QUOTE_RENDERER_CLASS", "NEMO_billing.quotes.renderers.PDFQuoteRenderer")
    assert isinstance(renderer_class, str)
    pkg, attr = renderer_class.rsplit(".", 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret()


quote_renderer_class = get_quote_renderer_class()
