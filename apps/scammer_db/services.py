from datetime import timedelta

from django.db import transaction
from django.db.models import Count, Max, Min
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.users.phone import build_phone_fields, phone_lookup

from .models import CommunityReport, ScammerNumber


def find_number(phone):
    return ScammerNumber.objects.filter(phone_hash=phone_lookup(phone)).first()


@transaction.atomic
def create_report(*, user, target_type, target_value, **report_data):
    number = None
    if target_type == CommunityReport.TargetType.PHONE:
        phone_fields = build_phone_fields(target_value)
        number, _ = ScammerNumber.objects.get_or_create(
            phone_hash=phone_fields["phone_hash"],
            defaults={
                "phone_encrypted": phone_fields["phone_encrypted"],
                "phone_masked": phone_fields["phone_masked"],
            },
        )
        normalized_target = phone_fields["phone_masked"]
    else:
        normalized_target = target_value.strip()

    duplicate_after = timezone.now() - timedelta(hours=24)
    duplicate_filter = {
        "user": user,
        "target_type": target_type,
        "created_at__gte": duplicate_after,
    }
    if number:
        duplicate_filter["scammer_number"] = number
    else:
        duplicate_filter["target_value__iexact"] = normalized_target
    if CommunityReport.objects.filter(**duplicate_filter).exists():
        raise ValidationError("You have already reported this target in the last 24 hours.")
    return CommunityReport.objects.create(
        user=user,
        scammer_number=number,
        target_type=target_type,
        target_value=normalized_target,
        **report_data,
    )


def recalculate_number(number):
    aggregate = number.reports.filter(status=CommunityReport.Status.APPROVED).aggregate(
        count=Count("id"),
        first=Min("created_at"),
        last=Max("created_at"),
    )
    count = aggregate["count"]
    number.approved_reports_count = count
    number.first_reported_at = aggregate["first"]
    number.last_reported_at = aggregate["last"]
    if number.status != ScammerNumber.Status.VERIFIED_SCAMMER:
        if count >= 4:
            number.status = ScammerNumber.Status.SCAMMER
        elif count >= 1:
            number.status = ScammerNumber.Status.SUSPICIOUS
        else:
            number.status = ScammerNumber.Status.REPORTED
    number.save(
        update_fields=[
            "approved_reports_count",
            "first_reported_at",
            "last_reported_at",
            "status",
            "updated_at",
        ]
    )
    return number


@transaction.atomic
def moderate_report(*, report, moderator, status, moderator_comment=""):
    locked_report = CommunityReport.objects.select_for_update().select_related(
        "scammer_number"
    ).get(id=report.id)
    locked_report.status = status
    locked_report.moderator_comment = moderator_comment
    locked_report.moderated_by = moderator
    locked_report.moderated_at = timezone.now()
    locked_report.save(
        update_fields=[
            "status",
            "moderator_comment",
            "moderated_by",
            "moderated_at",
            "updated_at",
        ]
    )
    if locked_report.scammer_number_id:
        recalculate_number(locked_report.scammer_number)
    return locked_report


@transaction.atomic
def set_verified_status(*, number, moderator, verified):
    locked_number = ScammerNumber.objects.select_for_update().get(id=number.id)
    if verified:
        locked_number.status = ScammerNumber.Status.VERIFIED_SCAMMER
        locked_number.verified_by = moderator
        locked_number.verified_at = timezone.now()
        locked_number.save(
            update_fields=[
                "status",
                "verified_by",
                "verified_at",
                "updated_at",
            ]
        )
    else:
        locked_number.verified_by = None
        locked_number.verified_at = None
        locked_number.status = ScammerNumber.Status.REPORTED
        locked_number.save(
            update_fields=[
                "status",
                "verified_by",
                "verified_at",
                "updated_at",
            ]
        )
        recalculate_number(locked_number)
    return locked_number
