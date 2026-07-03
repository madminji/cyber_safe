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
def test_blocked_user_cannot_verify_otp(client):
    user = User.objects.create_user(
        phone="+998901234567",
        full_name="Blocked",
        is_active=False,
        is_verified=True,
    )
    assert user
    request_response = client.post(
        reverse("request-otp"),
        {"phone": "+998901234567"},
        format="json",
    )

    verify_response = client.post(
        reverse("verify-otp"),
        {
            "challenge_id": request_response.data["challenge_id"],
            "phone": "+998901234567",
            "code": request_response.data["development_otp"],
        },
        format="json",
    )

    assert verify_response.status_code == 400
    assert "blocked" in str(verify_response.data).lower()


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
    assert profile_response.data["rank"] == 1
    assert "phone_encrypted" not in profile_response.data


@pytest.mark.django_db
def test_profile_rank_uses_points(client):
    leader = User.objects.create_user(
        phone="+998901111111",
        full_name="Leader",
        points=50,
        is_verified=True,
    )
    current = User.objects.create_user(
        phone="+998902222222",
        full_name="Current",
        points=20,
        is_verified=True,
    )
    inactive = User.objects.create_user(
        phone="+998903333333",
        full_name="Inactive",
        points=100,
        is_active=False,
        is_verified=True,
    )
    assert leader and inactive
    client.force_authenticate(current)

    response = client.get(reverse("me"))

    assert response.status_code == 200
    assert response.data["rank"] == 2


@pytest.mark.django_db
def test_public_leaderboard_lists_active_users_without_full_phone(client):
    User.objects.create_user(
        phone="+998901111111",
        full_name="Leader",
        points=50,
        is_verified=True,
    )
    User.objects.create_user(
        phone="+998902222222",
        full_name="",
        points=20,
        is_verified=True,
    )
    User.objects.create_user(
        phone="+998903333333",
        full_name="Inactive",
        points=100,
        is_active=False,
        is_verified=True,
    )

    response = client.get(reverse("user-leaderboard"))

    assert response.status_code == 200
    assert [row["points"] for row in response.data] == [50, 20]
    assert response.data[0]["rank"] == 1
    assert response.data[1]["user_name"] == "+99890***2222"
    assert "+998902222222" not in str(response.data)


@pytest.mark.django_db
def test_admin_can_manage_users(client):
    admin = User.objects.create_user(
        phone="+998901111111",
        full_name="Admin",
        role=User.Role.ADMIN,
        is_verified=True,
    )
    target = User.objects.create_user(
        phone="+998902222222",
        full_name="Target",
        is_verified=True,
    )
    citizen = User.objects.create_user(
        phone="+998903333333",
        full_name="Citizen",
        is_verified=True,
    )

    client.force_authenticate(citizen)
    forbidden = client.get(reverse("admin-user-list"))
    assert forbidden.status_code == 403

    client.force_authenticate(admin)
    listed = client.get(reverse("admin-user-list"))
    assert listed.status_code == 200
    assert any(item["id"] == str(target.id) for item in listed.data)

    updated = client.patch(
        reverse("admin-user-detail", kwargs={"user_id": target.id}),
        {
            "role": User.Role.MODERATOR,
            "points": 77,
            "is_active": False,
        },
        format="json",
    )

    assert updated.status_code == 200
    assert updated.data["role"] == User.Role.MODERATOR
    assert updated.data["points"] == 77
    assert updated.data["is_active"] is False
    target.refresh_from_db()
    assert target.is_staff is True


@pytest.mark.django_db
def test_admin_cannot_deactivate_or_demote_self(client):
    admin = User.objects.create_user(
        phone="+998901111111",
        full_name="Admin",
        role=User.Role.ADMIN,
        is_verified=True,
    )
    client.force_authenticate(admin)

    response = client.patch(
        reverse("admin-user-detail", kwargs={"user_id": admin.id}),
        {"role": User.Role.CITIZEN, "is_active": False},
        format="json",
    )

    assert response.status_code == 400
