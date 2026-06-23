from io import BytesIO
from pathlib import Path

import qrcode
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


def register_certificate_font():
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            pdfmetrics.registerFont(TTFont("CyberSafeFont", str(path)))
            return "CyberSafeFont"
    return "Helvetica"


def build_certificate_pdf(certificate):
    output = BytesIO()
    width, height = landscape(A4)
    pdf = canvas.Canvas(output, pagesize=(width, height))
    font = register_certificate_font()
    verification_url = (
        f"{settings.PUBLIC_SITE_URL.rstrip('/')}/api/v1/certificates/{certificate.id}/"
    )

    pdf.setFillColor(colors.HexColor("#F5F8FC"))
    pdf.rect(0, 0, width, height, fill=1, stroke=0)
    pdf.setStrokeColor(colors.HexColor("#155EEF"))
    pdf.setLineWidth(4)
    pdf.rect(24, 24, width - 48, height - 48, fill=0, stroke=1)

    pdf.setFillColor(colors.HexColor("#0B1F3A"))
    pdf.setFont(font, 25)
    pdf.drawCentredString(width / 2, height - 105, "CyberSafe Uzbekistan")
    pdf.setFont(font, 16)
    pdf.drawCentredString(width / 2, height - 145, "СЕРТИФИКАТ")

    style = ParagraphStyle(
        name="certificate",
        fontName=font,
        fontSize=18,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0B1F3A"),
    )
    full_name = certificate.user.full_name or certificate.user.phone_masked
    body = Paragraph(
        (
            f"Настоящим подтверждается, что<br/><b>{full_name}</b><br/>"
            f"успешно прошёл(ла) тест по цифровой безопасности.<br/>"
            f"Результат: <b>{certificate.score}%</b> · Уровень: "
            f"<b>{certificate.level.upper()}</b>"
        ),
        style,
    )
    body.wrapOn(pdf, width - 180, 220)
    body.drawOn(pdf, 90, height / 2 - 80)

    qr_image = qrcode.make(verification_url)
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    pdf.drawImage(
        ImageReader(qr_buffer),
        width - 150,
        65,
        width=80,
        height=80,
        preserveAspectRatio=True,
        mask="auto",
    )

    pdf.setFont(font, 9)
    pdf.drawString(65, 88, f"ID: {certificate.id}")
    pdf.drawString(65, 70, f"Дата выдачи: {certificate.issued_at:%d.%m.%Y}")
    pdf.drawRightString(width - 65, 48, "Проверка подлинности по QR-коду")
    pdf.showPage()
    pdf.save()
    output.seek(0)
    return output

