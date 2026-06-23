from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

required_secrets = {
    "DJANGO_SECRET_KEY": SECRET_KEY,  # noqa: F405
    "PHONE_ENCRYPTION_KEY": PHONE_ENCRYPTION_KEY,  # noqa: F405
    "PHONE_LOOKUP_SECRET": PHONE_LOOKUP_SECRET,  # noqa: F405
    "OTP_HASH_SECRET": OTP_HASH_SECRET,  # noqa: F405
    "ANALYZER_HASH_SECRET": ANALYZER_HASH_SECRET,  # noqa: F405
}
for secret_name, value in required_secrets.items():
    if not value or value.startswith(("unsafe-", "change-", "replace-")):
        raise ImproperlyConfigured(f"{secret_name} must be configured for production")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
OTP_ECHO_IN_RESPONSE = False
