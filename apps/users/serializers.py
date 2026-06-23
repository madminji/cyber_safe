from rest_framework import serializers

from .models import User
from .phone import normalize_phone
from .services import create_otp_challenge, verify_otp_challenge


class RequestOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    region = serializers.CharField(max_length=30, required=False, allow_blank=True)
    language = serializers.ChoiceField(choices=User.Language.choices, default=User.Language.RUSSIAN)

    def validate_phone(self, value):
        try:
            return normalize_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def create(self, validated_data):
        return create_otp_challenge(**validated_data)


class VerifyOTPSerializer(serializers.Serializer):
    challenge_id = serializers.UUIDField()
    phone = serializers.CharField(max_length=20)
    code = serializers.RegexField(r"^\d{6}$")

    def validate_phone(self, value):
        try:
            return normalize_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def create(self, validated_data):
        return verify_otp_challenge(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone_masked",
            "full_name",
            "region",
            "language",
            "role",
            "points",
            "is_verified",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "phone_masked",
            "role",
            "points",
            "is_verified",
            "date_joined",
        ]


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

