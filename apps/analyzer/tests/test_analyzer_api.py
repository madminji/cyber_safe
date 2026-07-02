import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.analyzer.models import AnalysisLog, ThreatDomain


@pytest.mark.django_db
def test_safe_https_url_has_low_risk_and_content_is_not_stored():
    url = "https://example.com/help"
    response = APIClient().post(reverse("analyzer-url"), {"url": url}, format="json")

    assert response.status_code == 200
    assert response.data["verdict"] == AnalysisLog.Verdict.SAFE
    log = AnalysisLog.objects.get()
    assert log.content_hash != url
    assert not hasattr(log, "content")


@pytest.mark.django_db
def test_known_threat_domain_is_dangerous():
    ThreatDomain.objects.create(
        domain="fake-bank.example",
        category=ThreatDomain.Category.FAKE_BANK,
    )

    response = APIClient().post(
        reverse("analyzer-url"),
        {"url": "https://fake-bank.example/login"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["verdict"] == AnalysisLog.Verdict.DANGEROUS
    assert response.data["risk_score"] == 100
    assert "known_threat" in response.data["signals"]


@pytest.mark.django_db
def test_url_with_userinfo_ip_and_http_is_dangerous():
    response = APIClient().post(
        reverse("analyzer-url"),
        {"url": "http://payme.uz@192.168.1.10/secure/login"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["verdict"] == AnalysisLog.Verdict.DANGEROUS
    assert {"no_https", "userinfo", "ip_host"}.issubset(response.data["signals"])


@pytest.mark.django_db
def test_sms_requesting_code_and_money_is_dangerous():
    response = APIClient().post(
        reverse("analyzer-sms"),
        {
            "text": (
                "Срочно! Ваша карта будет заблокирована. Назовите SMS-код "
                "и переведите деньги на безопасный счёт."
            )
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["verdict"] == AnalysisLog.Verdict.DANGEROUS
    assert response.data["risk_score"] >= 60
    assert {"urgency", "secret_request", "money"}.issubset(response.data["signals"])


@pytest.mark.django_db
def test_neutral_sms_is_not_declared_guaranteed_safe():
    response = APIClient().post(
        reverse("analyzer-sms"),
        {"text": "Встречаемся сегодня в 18:00 у входа."},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["verdict"] == AnalysisLog.Verdict.SAFE
    assert "не гарантирует" in response.data["reasons"][0].lower() or (
        "не передавайте" in response.data["reasons"][0].lower()
    )


@pytest.mark.django_db
def test_remote_access_and_investment_signals_are_detected():
    response = APIClient().post(
        reverse("analyzer-sms"),
        {
            "text": (
                "Установите AnyDesk и покажите экран. Затем внесите депозит: "
                "мы гарантируем доход без риска."
            )
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["verdict"] == AnalysisLog.Verdict.DANGEROUS
    assert {"remote_access", "investment"}.issubset(response.data["signals"])


@pytest.mark.django_db
def test_local_brand_impersonation_in_url_is_detected():
    response = APIClient().post(
        reverse("analyzer-url"),
        {"url": "https://payme-secure-login.example/confirm"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["verdict"] in {
        AnalysisLog.Verdict.SUSPICIOUS,
        AnalysisLog.Verdict.DANGEROUS,
    }
    assert "brand_impersonation" in response.data["signals"]


@pytest.mark.django_db
def test_uzbek_language_returns_localized_reasons_and_privacy():
    response = APIClient().post(
        reverse("analyzer-sms"),
        {
            "text": "Zudlik bilan SMS kodni ayting va pul o'tkazing.",
            "language": "uz",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["verdict"] == AnalysisLog.Verdict.DANGEROUS
    assert any("shoshilinch" in reason for reason in response.data["reasons"])
    assert "Mazmun saqlanmadi" in response.data["privacy"]


@pytest.mark.django_db
def test_analyzer_rejects_unknown_language():
    response = APIClient().post(
        reverse("analyzer-url"),
        {"url": "https://example.com", "language": "en"},
        format="json",
    )

    assert response.status_code == 400
    assert "language" in response.data["error"]["details"]


@pytest.mark.django_db
def test_analyzer_rate_limit():
    client = APIClient()
    for _ in range(10):
        response = client.post(
            reverse("analyzer-sms"),
            {"text": "Обычное сообщение для проверки лимита."},
            format="json",
            REMOTE_ADDR="10.0.0.8",
        )
        assert response.status_code == 200

    limited = client.post(
        reverse("analyzer-sms"),
        {"text": "Ещё одно обычное сообщение."},
        format="json",
        REMOTE_ADDR="10.0.0.8",
    )
    assert limited.status_code == 429
