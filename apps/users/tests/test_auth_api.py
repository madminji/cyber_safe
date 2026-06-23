import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import OTPChallenge, User


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_request_and_verify_otp_creates_user(client):
    request_response = client.post(
        reverse("request-otp"),
        {
            "phone": "+998 90 123-45-67",
            "full_name": "Test Citizen",
            "language": "uz",
        },
        format="json",
    )

    assert request_response.status_code == 201
    assert "development_otp" in request_response.data
    challenge = OTPChallenge.objects.get(id=request_response.data["challenge_id"])
    assert challenge.phone_masked == "+99890***4567"
    assert "+998901234567" not in challenge.phone_encrypted

    verify_response = client.post(
        reverse("verify-otp"),
        {
            "challenge_id": challenge.id,
            "phone": "+998901234567",
            "code": request_response.data["development_otp"],
        },
        format="json",
    )

    assert verify_response.status_code == 200
    assert "access" in verify_response.data
    assert "refresh" in verify_response.data
    user = User.objects.get()
    assert user.phone == "+998901234567"
    assert user.phone_masked == "+99890***4567"
    assert user.is_verified is True


@pytest.mark.django_db
def test_wrong_otp_increments_attempts(client):
    response = client.post(
        reverse("request-otp"),
        {"phone": "+998901234567"},
        format="json",
    )
    challenge_id = response.data["challenge_id"]

    verify_response = client.post(
        reverse("verify-otp"),
        {
            "challenge_id": challenge_id,
            "phone": "+998901234567",
            "code": "000000",
        },
        format="json",
    )

    assert verify_response.status_code == 400
    challenge = OTPChallenge.objects.get(id=challenge_id)
    assert challenge.attempts == 1


@pytest.mark.django_db
def test_authenticated_user_can_read_profile(client):
    otp_response = client.post(
        reverse("request-otp"),
        {"phone": "+998901234567"},
        format="json",
    )
    auth_response = client.post(
        reverse("verify-otp"),
        {
            "challenge_id": otp_response.data["challenge_id"],
            "phone": "+998901234567",
            "code": otp_response.data["development_otp"],
        },
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_response.data['access']}")

    profile_response = client.get(reverse("me"))

    assert profile_response.status_code == 200
    assert profile_response.data["phone_masked"] == "+99890***4567"
    assert "phone_encrypted" not in profile_response.data

