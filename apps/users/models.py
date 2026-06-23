import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager
from .phone import decrypt_phone


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CITIZEN = "citizen", "Citizen"
        MODERATOR = "moderator", "Moderator"
        ADMIN = "admin", "Admin"

    class Language(models.TextChoices):
        RUSSIAN = "ru", "Русский"
        UZBEK = "uz", "O‘zbekcha"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_hash = models.CharField(max_length=64, unique=True)
    phone_encrypted = models.TextField()
    phone_masked = models.CharField(max_length=13)
    full_name = models.CharField(max_length=150, blank=True)
    region = models.CharField(max_length=30, blank=True)
    language = models.CharField(max_length=5, choices=Language.choices, default=Language.RUSSIAN)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CITIZEN)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    points = models.PositiveIntegerField(default=0)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_hash"
    REQUIRED_FIELDS = []

    @property
    def phone(self):
        return decrypt_phone(self.phone_encrypted)

    def __str__(self):
        return self.phone_masked


class OTPChallenge(models.Model):
    class Purpose(models.TextChoices):
        AUTHENTICATE = "authenticate", "Authenticate"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_hash = models.CharField(max_length=64, db_index=True)
    phone_encrypted = models.TextField()
    phone_masked = models.CharField(max_length=13)
    code_hash = models.CharField(max_length=64)
    purpose = models.CharField(
        max_length=20,
        choices=Purpose.choices,
        default=Purpose.AUTHENTICATE,
    )
    full_name = models.CharField(max_length=150, blank=True)
    region = models.CharField(max_length=30, blank=True)
    language = models.CharField(
        max_length=5,
        choices=User.Language.choices,
        default=User.Language.RUSSIAN,
    )
    attempts = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["phone_hash", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.phone_masked} ({self.created_at:%Y-%m-%d %H:%M})"

