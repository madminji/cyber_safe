import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import Throttled, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTPChallenge, User
from .phone import build_phone_fields, phone_lookup


def hash_otp(challenge_id, code):
    payload = f"{challenge_id}:{code}".encode()
    return hmac.new(settings.OTP_HASH_SECRET.encode(), payload, hashlib.sha256).hexdigest()


def enforce_otp_request_limit(phone_hash_value):
    key = f"otp-request:{phone_hash_value}"
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=settings.OTP_REQUEST_WINDOW_SECONDS)
        count = 1
    if count > settings.OTP_REQUEST_LIMIT:
        raise Throttled(
            detail="Too many OTP requests. Try again later.",
            wait=settings.OTP_REQUEST_WINDOW_SECONDS,
        )


def send_otp(phone, code):
    # Replace with the selected Uzbekistan SMS gateway adapter.
    # Deliberately avoids logging the phone number or OTP.
    return None


@transaction.atomic
def create_otp_challenge(*, phone, full_name="", region="", language="ru"):
    phone_fields = build_phone_fields(phone)
    enforce_otp_request_limit(phone_fields["phone_hash"])

    OTPChallenge.objects.filter(
        phone_hash=phone_fields["phone_hash"],
        used_at__isnull=True,
    ).update(used_at=timezone.now())

    challenge = OTPChallenge(
        **phone_fields,
        full_name=full_name,
        region=region,
        language=language,
        expires_at=timezone.now() + timedelta(seconds=settings.OTP_TTL_SECONDS),
    )
    code = f"{secrets.randbelow(1_000_000):06d}"
    challenge.code_hash = hash_otp(challenge.id, code)
    challenge.save()
    send_otp(phone, code)
    return challenge, code


def verify_otp_challenge(*, challenge_id, phone, code):
    with transaction.atomic():
        try:
            challenge = OTPChallenge.objects.select_for_update().get(id=challenge_id)
        except OTPChallenge.DoesNotExist as exc:
            raise ValidationError("Invalid or expired OTP challenge.") from exc

        now = timezone.now()
        supplied_phone_hash = phone_lookup(phone)
        invalid = (
            challenge.used_at is not None
            or challenge.expires_at <= now
            or challenge.phone_hash != supplied_phone_hash
            or challenge.attempts >= settings.OTP_MAX_ATTEMPTS
        )
        if invalid:
            raise ValidationError("Invalid or expired OTP challenge.")

        valid_code = hmac.compare_digest(challenge.code_hash, hash_otp(challenge.id, code))
        if not valid_code:
            challenge.attempts += 1
            challenge.save(update_fields=["attempts"])
            invalid_code = True
        else:
            invalid_code = False
            challenge.used_at = now
            challenge.save(update_fields=["used_at"])

        if not invalid_code:
            user, created = User.objects.get_or_create(
                phone_hash=challenge.phone_hash,
                defaults={
                    "phone_encrypted": challenge.phone_encrypted,
                    "phone_masked": challenge.phone_masked,
                    "full_name": challenge.full_name,
                    "region": challenge.region,
                    "language": challenge.language,
                    "is_verified": True,
                },
            )
            if not created and not user.is_verified:
                user.is_verified = True
                user.save(update_fields=["is_verified", "updated_at"])

    if invalid_code:
        raise ValidationError("Invalid or expired OTP challenge.")

    refresh = RefreshToken.for_user(user)
    return user, {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
