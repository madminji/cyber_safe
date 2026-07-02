from datetime import date

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.scammer_db.models import CommunityReport, ScammerNumber
from apps.users.models import User


@pytest.fixture
def citizen():
    return User.objects.create_user(
        phone="+998901234567",
        full_name="Citizen",
        is_verified=True,
    )


@pytest.fixture
def moderator():
    return User.objects.create_user(
        phone="+998911234567",
        full_name="Moderator",
        role=User.Role.MODERATOR,
        is_verified=True,
    )


def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def report_payload(phone="+998931112233"):
    return {
        "phone": phone,
        "scam_type": CommunityReport.ScamType.BANK_CALL,
        "incident_date": date.today().isoformat(),
        "story": "Звонивший представился сотрудником банка и запросил код из SMS.",
        "region": "tashkent",
        "damage_amount": "100000.00",
    }


@pytest.mark.django_db
def test_unknown_number_is_not_claimed_safe():
    response = APIClient().get(
        reverse("scammer-check"),
        {"phone": "+998931112233"},
    )

    assert response.status_code == 200
    assert response.data["found"] is False
    assert response.data["status"] == "not_found"
    assert "safe" in response.data["message"].lower()


@pytest.mark.django_db
def test_citizen_can_report_and_pending_report_is_not_public(citizen):
    client = authenticated_client(citizen)
    created = client.post(reverse("scammer-report-create"), report_payload(), format="json")

    assert created.status_code == 201
    assert created.data["status"] == CommunityReport.Status.PENDING
    number = ScammerNumber.objects.get()
    assert "+998931112233" not in number.phone_encrypted

    public = APIClient().get(reverse("scammer-check"), {"phone": "+998931112233"})
    assert public.data["found"] is False


@pytest.mark.django_db
def test_duplicate_report_within_24_hours_is_rejected(citizen):
    client = authenticated_client(citizen)
    first = client.post(
        reverse("scammer-report-create"),
        report_payload(),
        format="json",
    )
    assert first.status_code == 201

    duplicate = client.post(
        reverse("scammer-report-create"),
        report_payload(),
        format="json",
    )

    assert duplicate.status_code == 400
    assert CommunityReport.objects.count() == 1


@pytest.mark.django_db
def test_moderator_approval_makes_number_public(citizen, moderator):
    citizen_client = authenticated_client(citizen)
    created = citizen_client.post(
        reverse("scammer-report-create"),
        report_payload(),
        format="json",
    )
    report_id = created.data["id"]

    moderator_client = authenticated_client(moderator)
    moderation = moderator_client.patch(
        reverse("scammer-moderation-detail", kwargs={"report_id": report_id}),
        {"status": CommunityReport.Status.APPROVED, "moderator_comment": "Проверено"},
        format="json",
    )

    assert moderation.status_code == 200
    public = APIClient().get(reverse("scammer-check"), {"phone": "+998931112233"})
    assert public.status_code == 200
    assert public.data["found"] is True
    assert public.data["status"] == ScammerNumber.Status.SUSPICIOUS
    assert public.data["approved_reports_count"] == 1
    assert "reporter_id" not in public.data


@pytest.mark.django_db
def test_four_approved_reports_mark_number_as_scammer(moderator):
    moderator_client = authenticated_client(moderator)
    for index in range(4):
        user = User.objects.create_user(
            phone=f"+99890{2000000 + index:07d}",
            full_name=f"Citizen {index}",
            is_verified=True,
        )
        created = authenticated_client(user).post(
            reverse("scammer-report-create"),
            report_payload(),
            format="json",
        )
        moderator_client.patch(
            reverse(
                "scammer-moderation-detail",
                kwargs={"report_id": created.data["id"]},
            ),
            {"status": CommunityReport.Status.APPROVED},
            format="json",
        )

    number = ScammerNumber.objects.get()
    assert number.status == ScammerNumber.Status.SCAMMER
    assert number.approved_reports_count == 4


@pytest.mark.django_db
def test_citizen_cannot_access_moderation(citizen):
    response = authenticated_client(citizen).get(reverse("scammer-moderation-list"))

    assert response.status_code == 403

    numbers_response = authenticated_client(citizen).get(
        reverse("scammer-moderation-number-list")
    )
    assert numbers_response.status_code == 403


@pytest.mark.django_db
def test_moderation_summary_counts_queue(citizen, moderator):
    authenticated_client(citizen).post(
        reverse("scammer-report-create"),
        report_payload(),
        format="json",
    )

    response = authenticated_client(moderator).get(
        reverse("scammer-moderation-summary")
    )

    assert response.status_code == 200
    assert response.data["pending"] == 1
    assert response.data["approved"] == 0
    assert response.data["reports_today"] == 1


@pytest.mark.django_db
def test_moderator_report_contains_number_state(citizen, moderator):
    authenticated_client(citizen).post(
        reverse("scammer-report-create"),
        report_payload(),
        format="json",
    )

    response = authenticated_client(moderator).get(
        reverse("scammer-moderation-list"),
        {"status": "pending"},
    )

    assert response.status_code == 200
    report = response.data[0]
    assert report["number_status"] == ScammerNumber.Status.REPORTED
    assert report["approved_reports_count"] == 0
    assert report["number_verified"] is False
    assert report["reporter_name"] == citizen.full_name


@pytest.mark.django_db
def test_approved_number_is_visible_in_moderation_number_registry(citizen, moderator):
    created = authenticated_client(citizen).post(
        reverse("scammer-report-create"),
        report_payload(),
        format="json",
    )
    moderator_client = authenticated_client(moderator)
    moderator_client.patch(
        reverse(
            "scammer-moderation-detail",
            kwargs={"report_id": created.data["id"]},
        ),
        {"status": CommunityReport.Status.APPROVED},
        format="json",
    )

    response = moderator_client.get(
        reverse("scammer-moderation-number-list"),
        {"status": ScammerNumber.Status.SUSPICIOUS},
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    number = response.data[0]
    assert number["phone_masked"] == "+99893***2233"
    assert number["status"] == ScammerNumber.Status.SUSPICIOUS
    assert number["approved_reports_count"] == 1
    assert number["number_verified"] is False
    assert number["scam_types"] == [CommunityReport.ScamType.BANK_CALL]
    assert number["latest_reports"][0]["id"] == created.data["id"]


@pytest.mark.django_db
def test_rejecting_approved_report_recalculates_status(citizen, moderator):
    created = authenticated_client(citizen).post(
        reverse("scammer-report-create"),
        report_payload(),
        format="json",
    )
    url = reverse(
        "scammer-moderation-detail",
        kwargs={"report_id": created.data["id"]},
    )
    moderator_client = authenticated_client(moderator)
    moderator_client.patch(
        url,
        {"status": CommunityReport.Status.APPROVED},
        format="json",
    )
    moderator_client.patch(
        url,
        {"status": CommunityReport.Status.REJECTED},
        format="json",
    )

    number = ScammerNumber.objects.get()
    assert number.status == ScammerNumber.Status.REPORTED
    assert number.approved_reports_count == 0


@pytest.mark.django_db
def test_stats_only_include_approved_reports(citizen, moderator):
    created = authenticated_client(citizen).post(
        reverse("scammer-report-create"),
        report_payload(),
        format="json",
    )
    stats_before = APIClient().get(reverse("scammer-stats"))
    assert stats_before.data["approved_reports"] == 0

    authenticated_client(moderator).patch(
        reverse(
            "scammer-moderation-detail",
            kwargs={"report_id": created.data["id"]},
        ),
        {"status": CommunityReport.Status.APPROVED},
        format="json",
    )
    stats_after = APIClient().get(reverse("scammer-stats"))

    assert stats_after.status_code == 200
    assert stats_after.data["approved_reports"] == 1
    assert stats_after.data["by_region"][0]["region"] == "tashkent"


@pytest.mark.django_db
def test_moderator_can_verify_and_unverify_number(citizen, moderator):
    created = authenticated_client(citizen).post(
        reverse("scammer-report-create"),
        report_payload(),
        format="json",
    )
    report = CommunityReport.objects.get(id=created.data["id"])
    client = authenticated_client(moderator)
    url = reverse(
        "scammer-number-verification",
        kwargs={"number_id": report.scammer_number_id},
    )

    verified = client.patch(url, {"verified": True}, format="json")
    assert verified.status_code == 200
    assert verified.data["status"] == ScammerNumber.Status.VERIFIED_SCAMMER

    unverified = client.patch(url, {"verified": False}, format="json")
    assert unverified.status_code == 200
    assert unverified.data["status"] == ScammerNumber.Status.REPORTED
