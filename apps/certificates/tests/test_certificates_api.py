from io import BytesIO
from unittest.mock import patch

import pytest
from django.test import RequestFactory, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient

from apps.certificates.models import Certificate
from apps.certificates.serializers import CertificateSerializer
from apps.certificates.services import RU_CERTIFICATE, RU_RESULT, build_certificate_pdf
from apps.quiz.models import TestSession as QuizTestSession
from apps.users.models import User


@pytest.fixture
def certificate():
    user = User.objects.create_user(
        phone="+998901234567",
        full_name="Certificate Owner",
        is_verified=True,
    )
    session = QuizTestSession.objects.create(
        user=user,
        language="ru",
        status=QuizTestSession.Status.COMPLETED,
        score=90,
        level=QuizTestSession.Level.EXPERT,
    )
    return Certificate.objects.create(
        user=user,
        quiz_session=session,
        level=QuizTestSession.Level.EXPERT,
        score=90,
    )


@pytest.mark.django_db
def test_certificate_serializer_returns_public_verification_page(certificate):
    request = RequestFactory().get("/", HTTP_HOST="127.0.0.1:8000")

    data = CertificateSerializer(certificate, context={"request": request}).data

    assert data["verification_url"] == (
        f"http://127.0.0.1:3000/certificates/verify/{certificate.id}"
    )
    assert data["pdf_url"] == ""


@pytest.mark.django_db
def test_certificate_serializer_returns_pdf_url_to_owner(certificate):
    request = RequestFactory().get("/", HTTP_HOST="127.0.0.1:8000")
    request.user = certificate.user

    data = CertificateSerializer(certificate, context={"request": request}).data

    assert data["pdf_url"].endswith(f"/api/v1/certificates/{certificate.id}/pdf/")


@pytest.mark.django_db
@override_settings(PUBLIC_SITE_URL="https://cybersafe.example")
def test_certificate_pdf_qr_points_to_public_verification_page(certificate):
    with patch("apps.certificates.services.qrcode.make") as make_qr:

        def save_png(buffer, format):
            image = Image.new("RGB", (8, 8), "white")
            image.save(buffer, format=format)

        make_qr.return_value.save.side_effect = save_png

        build_certificate_pdf(certificate)

    make_qr.assert_called_once_with(
        f"https://cybersafe.example/certificates/verify/{certificate.id}"
    )


def test_certificate_pdf_has_russian_labels():
    assert RU_CERTIFICATE == "\u0421\u0415\u0420\u0422\u0418\u0424\u0418\u041a\u0410\u0422"
    assert RU_RESULT == "\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442"


@pytest.mark.django_db
def test_certificate_pdf_download_requires_owner_or_admin(certificate):
    url = reverse("certificate-pdf", kwargs={"certificate_id": certificate.id})
    anonymous = APIClient().get(url)
    assert anonymous.status_code == 401

    stranger = User.objects.create_user(
        phone="+998901111111",
        full_name="Stranger",
        is_verified=True,
    )
    stranger_client = APIClient()
    stranger_client.force_authenticate(stranger)
    forbidden = stranger_client.get(url)
    assert forbidden.status_code == 403

    owner_client = APIClient()
    owner_client.force_authenticate(certificate.user)
    owner_response = owner_client.get(url)
    assert owner_response.status_code == 200
    assert owner_response["content-type"] == "application/pdf"
