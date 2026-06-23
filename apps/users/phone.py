import hashlib
import hmac
import re

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

UZ_PHONE_PATTERN = re.compile(r"^\+998\d{9}$")


def normalize_phone(phone):
    normalized = re.sub(r"[\s\-()]", "", str(phone).strip())
    if normalized.startswith("998") and not normalized.startswith("+"):
        normalized = f"+{normalized}"
    if not UZ_PHONE_PATTERN.fullmatch(normalized):
        raise ValueError("Use Uzbekistan phone format +998XXXXXXXXX")
    return normalized


def phone_lookup(phone):
    normalized = normalize_phone(phone)
    return hmac.new(
        settings.PHONE_LOOKUP_SECRET.encode(),
        normalized.encode(),
        hashlib.sha256,
    ).hexdigest()


def encrypt_phone(phone):
    if not settings.PHONE_ENCRYPTION_KEY:
        raise ImproperlyConfigured("PHONE_ENCRYPTION_KEY is not configured")
    normalized = normalize_phone(phone)
    return Fernet(settings.PHONE_ENCRYPTION_KEY.encode()).encrypt(normalized.encode()).decode()


def decrypt_phone(token):
    try:
        return Fernet(settings.PHONE_ENCRYPTION_KEY.encode()).decrypt(token.encode()).decode()
    except (InvalidToken, ValueError) as exc:
        raise ValueError("Phone value cannot be decrypted") from exc


def mask_phone(phone):
    normalized = normalize_phone(phone)
    return f"{normalized[:6]}***{normalized[-4:]}"


def build_phone_fields(phone):
    normalized = normalize_phone(phone)
    return {
        "phone_hash": phone_lookup(normalized),
        "phone_encrypted": encrypt_phone(normalized),
        "phone_masked": mask_phone(normalized),
    }

