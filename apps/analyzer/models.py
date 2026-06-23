import uuid

from django.db import models


class AnalysisLog(models.Model):
    class ContentType(models.TextChoices):
        URL = "url", "URL"
        SMS = "sms", "SMS"

    class Verdict(models.TextChoices):
        SAFE = "safe", "No obvious risk detected"
        SUSPICIOUS = "suspicious", "Suspicious"
        DANGEROUS = "dangerous", "Dangerous"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_hash = models.CharField(max_length=64, db_index=True)
    content_type = models.CharField(max_length=10, choices=ContentType.choices)
    verdict = models.CharField(max_length=12, choices=Verdict.choices)
    risk_score = models.PositiveSmallIntegerField()
    reasons = models.JSONField(default=list)
    ip_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("content_type", "verdict", "-created_at")),
        ]


class ThreatDomain(models.Model):
    class Category(models.TextChoices):
        PHISHING = "phishing", "Phishing"
        MALWARE = "malware", "Malware"
        SCAM = "scam", "Scam"
        FAKE_BANK = "fake_bank", "Fake bank"

    domain = models.CharField(max_length=253, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    source = models.CharField(max_length=100, default="CyberSafe")
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.domain

