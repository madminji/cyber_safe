from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "test-secret-key-that-is-deliberately-longer-than-thirty-two-bytes"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "cybersafe-tests",
    }
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
PHONE_ENCRYPTION_KEY = "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
PHONE_LOOKUP_SECRET = "test-phone-secret"
OTP_HASH_SECRET = "test-otp-secret"
ANALYZER_HASH_SECRET = "test-analyzer-secret"
OPENROUTER_API_KEY = ""
OTP_ECHO_IN_RESPONSE = True
