import uuid

from django.conf import settings
from django.db import models


class ScammerNumber(models.Model):
    class Status(models.TextChoices):
        REPORTED = "reported", "Reported"
        SUSPICIOUS = "suspicious", "Suspicious"
        SCAMMER = "scammer", "Scammer"
        VERIFIED_SCAMMER = "verified_scammer", "Verified scammer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_hash = models.CharField(max_length=64, unique=True)
    phone_encrypted = models.TextField()
    phone_masked = models.CharField(max_length=13)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REPORTED,
    )
    approved_reports_count = models.PositiveIntegerField(default=0)
    first_reported_at = models.DateTimeField(null=True, blank=True)
    last_reported_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="verified_scammer_numbers",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone_masked


class CommunityReport(models.Model):
    class TargetType(models.TextChoices):
        PHONE = "phone", "Phone number"
        URL = "url", "Website or link"
        ACCOUNT = "account", "Messenger or social account"
        CARD = "card", "Card or bank account"
        OTHER = "other", "Other"

    class ScamType(models.TextChoices):
        BANK_CALL = "bank_call", "Fake bank call"
        SMS_CODE = "sms_code", "SMS code theft"
        MALWARE = "malware", "Malicious application"
        MARKETPLACE = "marketplace", "Marketplace fraud"
        PRIZE = "prize", "Fake prize"
        RELATIVE = "relative", "Fake relative"
        ROMANCE = "romance", "Romance scam"
        INVESTMENT = "investment", "Investment scam"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="scammer_reports",
        on_delete=models.PROTECT,
    )
    scammer_number = models.ForeignKey(
        ScammerNumber,
        related_name="reports",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    target_type = models.CharField(
        max_length=20,
        choices=TargetType.choices,
        default=TargetType.PHONE,
    )
    target_value = models.CharField(max_length=300, blank=True)
    scam_type = models.CharField(max_length=30, choices=ScamType.choices)
    incident_date = models.DateField()
    story = models.TextField(max_length=1000)
    region = models.CharField(max_length=30)
    damage_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    moderator_comment = models.CharField(max_length=500, blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="moderated_scammer_reports",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "-created_at")),
            models.Index(fields=("scam_type", "-created_at")),
            models.Index(fields=("region", "-created_at")),
        ]

    def __str__(self):
        target = self.scammer_number.phone_masked if self.scammer_number else self.target_value
        return f"{target} — {self.status}"
