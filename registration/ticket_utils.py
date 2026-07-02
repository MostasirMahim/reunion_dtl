"""
Generates the QR code + the official entry ticket PDF for a Registrant,
in the same visual spirit as the sample ticket provided (dashed border,
blue header, QR top-right, key/value info block).
"""
import io
import os

import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_FONT_REGULAR = "NotoBengali"
_FONT_BOLD = "NotoBengali"  # single weight variable font; reused as bold visually via size

if _FONT_REGULAR not in pdfmetrics.getRegisteredFontNames():
    pdfmetrics.registerFont(
        TTFont(_FONT_REGULAR, os.path.join(FONT_DIR, "NotoSansBengali-Regular.ttf"))
    )

NAVY = colors.HexColor("#0B3D7A")
GREY = colors.HexColor("#6B7280")
LIGHT_BG = colors.HexColor("#FFF8E6")
ORANGE = colors.HexColor("#D97706")


def build_verify_url(registrant):
    base_url = settings.SITE_BASE_URL.rstrip("/")
    return f"{base_url}/verify/{registrant.registration_id}/{registrant.verify_token}/"


def generate_qr_code(registrant):
    url = build_verify_url(registrant)
    qr = qrcode.QRCode(border=2, box_size=10)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    filename = f"{registrant.registration_id}.png"
    registrant.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
    return img


def generate_ticket_pdf(registrant):
    """Builds the entry ticket PDF and attaches it to registrant.ticket_pdf."""
    if not registrant.qr_code:
        generate_qr_code(registrant)

    buffer = io.BytesIO()
    width, height = A5
    c = canvas.Canvas(buffer, pagesize=A5)

    margin = 10 * mm
    card_x, card_y = margin, margin
    card_w, card_h = width - 2 * margin, height - 2 * margin

    # Dashed border card
    c.setDash(3, 3)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.2)
    c.roundRect(card_x, card_y, card_w, card_h, 8, stroke=1, fill=0)
    c.setDash()

    inner_x = card_x + 8 * mm
    y = card_y + card_h - 16 * mm

    # School name + event title
    c.setFillColor(NAVY)
    c.setFont("NotoBengali", 16)
    c.drawString(inner_x, y, settings.SCHOOL_NAME.upper())
    y -= 7 * mm
    c.setFillColor(GREY)
    c.setFont("NotoBengali", 11)
    c.drawString(inner_x, y, settings.EVENT_FULL_NAME)

    # OFFICIAL ENTRY TICKET banner
    y -= 9 * mm
    c.setFillColor(NAVY)
    c.roundRect(inner_x, y - 2 * mm, card_w - 16 * mm, 8 * mm, 4, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("NotoBengali", 10)
    c.drawCentredString(inner_x + (card_w - 16 * mm) / 2, y, "OFFICIAL ENTRY TICKET")

    # Divider
    y -= 10 * mm
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.8)
    c.line(inner_x, y, card_x + card_w - 8 * mm, y)

    # QR Code - top right
    qr_size = 30 * mm
    qr_x = card_x + card_w - 8 * mm - qr_size
    qr_y = y - qr_size + 2 * mm
    qr_img = ImageReader(registrant.qr_code.path)
    c.drawImage(qr_img, qr_x, qr_y, qr_size, qr_size)
    c.setFillColor(GREY)
    c.setFont("NotoBengali", 7)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 4 * mm, "Scan at the Gate")

    # Info block - left side
    y -= 9 * mm
    label_font = ("NotoBengali", 7.5)
    value_font_bold = ("NotoBengali", 11)
    value_font = ("NotoBengali", 12)

    def draw_field(label, value, dy, value_size=11):
        nonlocal y
        c.setFillColor(GREY)
        c.setFont(*label_font)
        c.drawString(inner_x, y, label)
        c.setFillColor(colors.black)
        c.setFont("NotoBengali", value_size)
        c.drawString(inner_x, y - 5 * mm, value)
        y -= dy

    draw_field("PARTICIPANT NAME", registrant.full_name, 11 * mm, 12)
    c.setFillColor(GREY)
    c.setFont(*label_font)
    c.drawString(inner_x, y, "REGISTRATION ID")
    c.setFillColor(NAVY)
    c.setFont("NotoBengali", 13)
    c.drawString(inner_x, y - 5.5 * mm, registrant.registration_id)
    y -= 11 * mm

    draw_field("MOBILE NUMBER", registrant.phone, 10 * mm, 11)
    draw_field("DEPARTMENT/CLASS & PASSING YEAR",
               f"{registrant.department_class} (Passing Year: {registrant.passing_year})", 10 * mm, 11)
    draw_field("T-SHIRT SIZE", registrant.get_tshirt_size_display(), 10 * mm, 11)

    # Bottom divider
    c.setStrokeColor(colors.HexColor("#E5E7EB"))
    c.setLineWidth(0.6)
    c.line(inner_x, y, card_x + card_w - 8 * mm, y)
    y -= 7 * mm

    # Event date & venue
    c.setFillColor(colors.black)
    c.setFont("NotoBengali", 9)
    c.drawString(inner_x, y, "Event Date:")
    c.setFont("NotoBengali", 9)
    c.drawString(inner_x + 18 * mm, y, settings.EVENT_DATE_TEXT)
    y -= 5.5 * mm
    c.setFont("NotoBengali", 9)
    c.drawString(inner_x, y, "Venue:")
    c.setFont("NotoBengali", 9)
    c.drawString(inner_x + 18 * mm, y, settings.EVENT_VENUE)

    # Highlight notice box
    y -= 9 * mm
    notice_h = 9 * mm
    c.setFillColor(LIGHT_BG)
    c.rect(inner_x, y - notice_h + 4*mm, card_w - 16 * mm, notice_h, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.setLineWidth(2)
    c.line(inner_x, y - notice_h + 4*mm, inner_x, y + 4*mm)
    c.setFont("NotoBengali", 8.5)
    c.drawString(inner_x + 4 * mm, y,
                 "Please bring a printed copy or show this PDF on your")
    c.drawString(inner_x + 4 * mm, y - 4 * mm, "mobile at the entry gate.")

    # Footer
    c.setFillColor(GREY)
    c.setFont("NotoBengali", 7)
    c.drawCentredString(card_x + card_w / 2, card_y + 11 * mm,
                         f"This ticket is valid only after successful payment confirmation.")
    c.drawCentredString(card_x + card_w / 2, card_y + 7 * mm,
                         f"{settings.EVENT_SHORT_NAME} | Developed for {settings.SCHOOL_NAME}")

    # Powered by BIDYATek strip
    c.setStrokeColor(colors.HexColor("#E5E7EB"))
    c.setLineWidth(0.5)
    c.line(inner_x, card_y + 4.5 * mm, card_x + card_w - 8 * mm, card_y + 4.5 * mm)
    c.setFillColor(NAVY)
    c.setFont("NotoBengali", 7.5)
    c.drawCentredString(card_x + card_w / 2, card_y + 1.5 * mm,
                         "Powered by BIDYATek — School Management Software")

    c.showPage()
    c.save()

    buffer.seek(0)
    filename = f"ticket-{registrant.registration_id}.pdf"
    registrant.ticket_pdf.save(filename, ContentFile(buffer.getvalue()), save=False)
    return buffer
