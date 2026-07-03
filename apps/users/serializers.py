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
    rank = serializers.SerializerMethodField()

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
            "rank",
            "is_verified",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "phone_masked",
            "role",
            "points",
            "rank",
            "is_verified",
            "date_joined",
        ]

    def get_rank(self, obj) -> int:
        return User.objects.filter(points__gt=obj.points, is_active=True).count() + 1


class AdminUserSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()

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
            "rank",
            "is_verified",
            "is_active",
            "is_staff",
            "date_joined",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "phone_masked",
            "rank",
            "is_staff",
            "date_joined",
            "updated_at",
        ]

    def get_rank(self, obj) -> int:
        return User.objects.filter(points__gt=obj.points, is_active=True).count() + 1

    def validate_role(self, value):
        request = self.context.get("request")
        if self.instance and request and self.instance.id == request.user.id:
            if value != self.instance.role:
                raise serializers.ValidationError("You cannot change your own role.")
        return value

    def validate_is_active(self, value):
        request = self.context.get("request")
        if self.instance and request and self.instance.id == request.user.id and not value:
            raise serializers.ValidationError("You cannot deactivate your own account.")
        return value

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        user.is_staff = user.role in {User.Role.MODERATOR, User.Role.ADMIN}
        user.save(update_fields=["is_staff", "updated_at"])
        return user


class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    user_name = serializers.CharField()
    points = serializers.IntegerField()
    is_current_user = serializers.BooleanField(default=False)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
