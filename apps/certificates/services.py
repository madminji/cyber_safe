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


RU_CERTIFICATE = "\u0421\u0415\u0420\u0422\u0418\u0424\u0418\u041a\u0410\u0422"
RU_CONFIRM = (
    "\u041d\u0430\u0441\u0442\u043e\u044f\u0449\u0438\u043c "
    "\u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0435\u0442\u0441\u044f, "
    "\u0447\u0442\u043e"
)
RU_PASSED = (
    "\u0443\u0441\u043f\u0435\u0448\u043d\u043e "
    "\u043f\u0440\u043e\u0448\u0451\u043b(\u043b\u0430) "
    "\u0442\u0435\u0441\u0442 \u043f\u043e "
    "\u0446\u0438\u0444\u0440\u043e\u0432\u043e\u0439 "
    "\u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438."
)
RU_RESULT = "\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442"
RU_LEVEL = "\u0423\u0440\u043e\u0432\u0435\u043d\u044c"
RU_ISSUED_AT = "\u0414\u0430\u0442\u0430 \u0432\u044b\u0434\u0430\u0447\u0438"
RU_QR_CHECK = (
    "\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 "
    "\u043f\u043e\u0434\u043b\u0438\u043d\u043d\u043e\u0441\u0442\u0438 "
    "\u043f\u043e QR-\u043a\u043e\u0434\u0443"
)


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
        f"{settings.PUBLIC_SITE_URL.rstrip('/')}/certificates/verify/{certificate.id}"
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
    pdf.drawCentredString(width / 2, height - 145, f"{RU_CERTIFICATE} / SERTIFIKAT")

    style = ParagraphStyle(
        name="certificate",
        fontName=font,
        fontSize=15,
        leading=23,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0B1F3A"),
    )
    full_name = certificate.user.full_name or certificate.user.phone_masked
    body = Paragraph(
        (
            f"{RU_CONFIRM}<br/><b>{full_name}</b><br/>"
            f"{RU_PASSED}<br/>"
            f"{RU_RESULT}: <b>{certificate.score}%</b> \u00b7 "
            f"{RU_LEVEL}: <b>{certificate.level.upper()}</b><br/><br/>"
            f"Ushbu sertifikat<br/><b>{full_name}</b><br/>"
            f"raqamli xavfsizlik bo\u2018yicha testni muvaffaqiyatli "
            f"topshirganini tasdiqlaydi.<br/>"
            f"Natija: <b>{certificate.score}%</b> \u00b7 "
            f"Daraja: <b>{certificate.level.upper()}</b>"
        ),
        style,
    )
    body.wrapOn(pdf, width - 180, 260)
    body.drawOn(pdf, 90, height / 2 - 110)

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
    pdf.drawString(
        65,
        70,
        f"{RU_ISSUED_AT} / Berilgan sana: {certificate.issued_at:%d.%m.%Y}",
    )
    pdf.drawRightString(
        width - 65,
        48,
        f"{RU_QR_CHECK} / QR-kod orqali tekshirish",
    )
    pdf.showPage()
    pdf.save()
    output.seek(0)
    return output
