from typing import Any, List, Optional, Tuple, Union

from django.db.models.fields.files import FieldFile
from django.utils.text import normalize_newlines
from reportlab.lib import colors, utils
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.fonts import tt2ps
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, KeepInFrame, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FONT_RIGHT = "Right"
FONT_CENTERED = "Centered"
HEADING_FONT = "Heading"
HEADING_FONT_RIGHT = f"{HEADING_FONT}{FONT_RIGHT}"
HEADING_FONT_CENTERED = f"{HEADING_FONT}{FONT_CENTERED}"
SMALL_FONT = "Small"
SMALL_FONT_RIGHT = f"{SMALL_FONT}{FONT_RIGHT}"
SMALL_FONT_CENTERED = f"{SMALL_FONT}{FONT_CENTERED}"

TABLE_STYLE_HEADER = [("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey), ("VALIGN", (0, 0), (-1, 0), "MIDDLE")]
TABLE_STYLE_HEADER_GRID = [("INNERGRID", (0, 0), (-1, 0), 0.25, colors.black)]
TABLE_STYLE_HEADER_BORDER = [("BOX", (0, 0), (-1, 0), 0.25, colors.black)]
TABLE_STYLE = [("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
TABLE_STYLE_GRID = [("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black)]
TABLE_STYLE_BORDER = [("BOX", (0, 0), (-1, -1), 0.25, colors.black)]
TABLE_STYLE_THICK_BORDER = [("BOX", (0, 0), (-1, -1), 0.5, colors.black)]


class PDFPageSize(object):
    A4 = A4
    Letter = letter


class PDFDocument:
    def __init__(
        self,
        buffer_bytes,
        pagesize: PDFPageSize,
        header_margin=20,
        side_margin=72,
        height_margin=72,
        right_margin=None,
        bottom_margin=None,
        footer_text: str = None,
        header_text: str = None,
        header_logo: FieldFile = None,
        document_author: str = None,
        document_title: str = None,
    ):
        # Header and footer values
        self.footer_text: str = footer_text
        self.header_text: str = header_text
        self.header_logo: FieldFile = header_logo
        # Metadata
        self.document_author = document_author
        self.document_title = document_title
        # Styles & PDF document properties
        self.styles: StyleSheet1 = get_or_create_styles()
        self.buffer = buffer_bytes
        self.pagesize = pagesize
        self.header_margin = header_margin
        self.width, self.height = self.pagesize
        self.pdf_doc = SimpleDocTemplate(
            buffer_bytes,
            leftMargin=side_margin,
            rightMargin=right_margin if right_margin else side_margin,
            topMargin=height_margin,
            bottomMargin=bottom_margin if bottom_margin else height_margin,
            pagesize=self.pagesize,
        )
        self.elements = []

    def add_page_break(self):
        self.elements.append(PageBreak())

    def add_space(self, width, height):
        self.elements.append(Spacer(width, height))

    def add_title(self, title, style: ParagraphStyle = None):
        title_style = style or self.styles["Title"]
        self.elements.append(Paragraph(title, title_style))

    def add_heading_paragraph(self, content, style: ParagraphStyle = None, fit=False, border=False):
        heading_style = style or self.styles[f"{HEADING_FONT}Bold18"]
        paragraph = Paragraph(keep_linebreaks(content), heading_style)
        max_height = heading_style.fontSize * 2 - 1
        if fit:
            paragraph = KeepInFrame(self.pdf_doc.width, max_height, [paragraph])
        if border:
            # using row height of less than 2 lines, to prevent wrapping
            paragraph = Table([[paragraph]], rowHeights=max_height)
            paragraph.setStyle(TableStyle(TABLE_STYLE))
            paragraph.setStyle(TableStyle(TABLE_STYLE_THICK_BORDER))
        self.elements.append(paragraph)

    def add_paragraph(self, content, style: ParagraphStyle = None):
        paragraph_style = style or self.styles[f"{SMALL_FONT}Base10"]
        self.elements.append(Paragraph(keep_linebreaks(content), paragraph_style))

    def add_table_key_value(
        self, data: List[Tuple[str, str]], col_width=None, key_style=None, value_style=None, padding=2
    ):
        table_key_style = key_style or self.styles[f"{SMALL_FONT}Bold12"]
        table_value_style = value_style or self.styles[f"{SMALL_FONT}Base12"]
        data_items = [
            [
                Paragraph(keep_linebreaks(item[0]), table_key_style),
                Paragraph(keep_linebreaks(item[1]), table_value_style),
            ]
            for item in data
        ]
        table_data = Table(data_items, colWidths=col_width, hAlign="LEFT")
        table_data.setStyle(TableStyle(TABLE_STYLE))
        table_data.setStyle(
            TableStyle([("TOPPADDING", (0, 0), (-1, -1), padding), ("BOTTOMPADDING", (0, 0), (-1, -1), padding)])
        )
        self.elements.append(table_data)

    def add_table(
        self, data: List[List[Any]], headers: List[Any] = None, col_width=None, grid=True, border=True, centered=True
    ):
        table_items = []
        repeat_rows = 0
        if headers:
            repeat_rows = 1
            table_items.append(get_table_items(headers, self.styles[f"{SMALL_FONT}Bold10"]))
        for row in data:
            row_data = []
            row_data.extend(get_table_items(row, self.styles[f"{SMALL_FONT}Base8"]))
            table_items.append(row_data)
        table_data = Table(
            table_items, colWidths=col_width, repeatRows=repeat_rows, hAlign="CENTER" if centered else "LEFT"
        )
        table_data.setStyle(TableStyle(TABLE_STYLE))
        if headers:
            table_data.setStyle(TableStyle(TABLE_STYLE_HEADER))
            if border:
                table_data.setStyle(TableStyle(TABLE_STYLE_HEADER_BORDER))
            if grid:
                table_data.setStyle(TableStyle(TABLE_STYLE_HEADER_GRID))
        add_table_style(table_data, grid, border)
        self.elements.append(table_data)

    def _get_resized_paragraph_to_fit_height(
        self, text, content_width, content_height, size=12, style_name=SMALL_FONT
    ) -> Tuple[Paragraph, int, int]:
        font_size = size
        while font_size > 0:
            paragraph = Paragraph(keep_linebreaks(text), self.styles[f"{style_name}Base{font_size}"])
            w, h = paragraph.wrap(content_width, content_height)
            if h <= content_height and w <= content_width:
                break
            else:
                font_size -= 1
        return paragraph, w, h

    def build(self):
        # Add those properties as attribute so we can use them in the canvas maker
        setattr(NumberedCanvas, "page_number_y", self.header_margin)
        setattr(NumberedCanvas, "page_number_x", self.width - self.header_margin)
        self.pdf_doc.build(
            self.elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer, canvasmaker=NumberedCanvas
        )

    def _header_footer(self, doc_canvas: canvas.Canvas, doc):
        # Save the state of our canvas so we can draw on it
        doc_canvas.saveState()
        # Set metadata
        doc_canvas.setAuthor(self.document_author)
        doc_canvas.setTitle(self.document_title)
        doc_canvas.setSubject(self.document_title)

        logo_width = 0
        if self.header_logo:
            max_height_logo = doc.topMargin - self.header_margin
            logo = get_image(self.header_logo.path, max_height_logo)
            logo_width, h = logo.wrap(doc.width, doc.topMargin)
            logo.drawOn(
                doc_canvas, self.header_margin, doc.height + doc.bottomMargin + doc.topMargin - h - self.header_margin
            )

        # Make sure headers and footer fit by adjusting the size if it doesn't.
        if self.header_text:
            header, w, h = self._get_resized_paragraph_to_fit_height(
                self.header_text,
                self.width - logo_width - self.header_margin * 3,
                doc.topMargin - self.header_margin,
                10,
                SMALL_FONT_RIGHT,
            )
            header.drawOn(
                doc_canvas,
                logo_width + self.header_margin * 2,
                doc.height + doc.bottomMargin + doc.topMargin - h - self.header_margin,
            )

        if self.footer_text:
            footer, w, h = self._get_resized_paragraph_to_fit_height(
                self.footer_text, doc.width - self.header_margin * 2, doc.bottomMargin - self.header_margin, 10
            )
            footer.drawOn(doc_canvas, self.header_margin, self.header_margin)

        # Release the canvas
        doc_canvas.restoreState()


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.Canvas = canvas.Canvas
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.setFontSize(8)
            self.draw_page_number(num_pages)
            self.Canvas.showPage(self)
        self.Canvas.save(self)

    def draw_page_number(self, page_count):
        page_number_x = self.page_number_x if hasattr(self, "page_number_x") else 211 * mm
        page_number_y = self.page_number_y if hasattr(self, "page_number_y") else 10
        self.drawRightString(page_number_x, page_number_y, "Page %d of %d" % (self._pageNumber, page_count))


def keep_linebreaks(text: str):
    value = normalize_newlines(text)
    return value.replace("\n", "<br/>")


def get_image(path, max_height):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = iw / float(ih)
    return Image(path, width=(max_height * aspect), height=max_height)


def add_table_style(table: Table, grid=True, border=True):
    if grid:
        table.setStyle(TableStyle(TABLE_STYLE_GRID))
    if border:
        table.setStyle(TableStyle(TABLE_STYLE_BORDER))


def get_table_items(items: List[Union[Tuple, str]], default_style) -> List[Paragraph]:
    row = []
    for row_item in items:
        if isinstance(row_item, tuple):
            text, style = row_item
            row.append(Paragraph(keep_linebreaks(text), style or default_style))
        elif isinstance(row_item, str):
            row.append(Paragraph(keep_linebreaks(row_item), default_style))
    return row


font_sheet: Optional[StyleSheet1] = None


def get_or_create_styles() -> StyleSheet1:
    global font_sheet
    if font_sheet:
        return font_sheet
    font_sheet = getSampleStyleSheet()
    base_font = font_sheet["Normal"].fontName
    font_styles = [
        ("Base", base_font),
        ("Bold", tt2ps(base_font, 1, 0)),
        ("Italic", tt2ps(base_font, 0, 1)),
        ("BoldItalic", tt2ps(base_font, 1, 1)),
    ]
    # Let's add a bunch of font for different sizes and styles
    # This method will add Small and Heading fonts with all sizes and styles, and LEFT, RIGHT, CENTER alignment
    for size in range(1, 30):
        for style_name, style_font in font_styles:
            for font_name, font_parent in [(SMALL_FONT, "Normal"), (HEADING_FONT, "Heading1")]:
                font_sheet.add(
                    ParagraphStyle(
                        name=f"{font_name}{style_name}{size}",
                        fontName=style_font,
                        parent=font_sheet[font_parent],
                        fontSize=size,
                        leading=round(size * 1.2),
                        alignment=TA_LEFT,
                    )
                )
                font_sheet.add(
                    ParagraphStyle(
                        name=f"{font_name}{FONT_RIGHT}{style_name}{size}",
                        parent=font_sheet[f"{font_name}{style_name}{size}"],
                        alignment=TA_RIGHT,
                    )
                )
                font_sheet.add(
                    ParagraphStyle(
                        name=f"{font_name}{FONT_CENTERED}{style_name}{size}",
                        parent=font_sheet[f"{font_name}{style_name}{size}"],
                        alignment=TA_CENTER,
                    )
                )
    return font_sheet
