from django.utils import timezone
from rest_framework import serializers

from apps.users.phone import decrypt_phone, normalize_phone

from .models import CommunityReport, ScammerNumber
from .services import create_report, moderate_report, set_verified_status


class PhoneCheckQuerySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)

    def validate_phone(self, value):
        try:
            return normalize_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class PublicReportStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityReport
        fields = ("scam_type", "incident_date", "story", "region")


class NumberCheckSerializer(serializers.ModelSerializer):
    reports = serializers.SerializerMethodField()
    scam_types = serializers.SerializerMethodField()

    class Meta:
        model = ScammerNumber
        fields = (
            "phone_masked",
            "status",
            "approved_reports_count",
            "scam_types",
            "first_reported_at",
            "last_reported_at",
            "reports",
        )

    def get_reports(self, obj) -> list[dict]:
        approved = obj.reports.filter(status=CommunityReport.Status.APPROVED)[:5]
        return PublicReportStorySerializer(approved, many=True).data

    def get_scam_types(self, obj) -> list[str]:
        return list(
            obj.reports.filter(status=CommunityReport.Status.APPROVED)
            .values_list("scam_type", flat=True)
            .distinct()
        )


class CreateReportSerializer(serializers.Serializer):
    target_type = serializers.ChoiceField(
        choices=CommunityReport.TargetType.choices,
        default=CommunityReport.TargetType.PHONE,
        required=False,
    )
    target_value = serializers.CharField(max_length=300, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    scam_type = serializers.ChoiceField(choices=CommunityReport.ScamType.choices)
    incident_date = serializers.DateField()
    story = serializers.CharField(min_length=20, max_length=1000)
    region = serializers.CharField(max_length=30)
    damage_amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=0,
    )

    def validate(self, attrs):
        target_type = attrs.get("target_type") or CommunityReport.TargetType.PHONE
        raw_target = attrs.get("target_value") or attrs.get("phone") or ""
        raw_target = raw_target.strip()
        if not raw_target:
            raise serializers.ValidationError(
                {"target_value": "Report target is required."}
            )
        if target_type == CommunityReport.TargetType.PHONE:
            try:
                attrs["target_value"] = normalize_phone(raw_target)
            except ValueError as exc:
                raise serializers.ValidationError({"target_value": str(exc)}) from exc
        else:
            attrs["target_value"] = raw_target
        attrs["target_type"] = target_type
        attrs.pop("phone", None)
        return attrs

    def validate_phone(self, value):
        try:
            return normalize_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_incident_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Incident date cannot be in the future.")
        return value

    def create(self, validated_data):
        return create_report(user=self.context["request"].user, **validated_data)


class MyReportSerializer(serializers.ModelSerializer):
    phone_masked = serializers.SerializerMethodField()
    target_display = serializers.SerializerMethodField()

    class Meta:
        model = CommunityReport
        fields = (
            "id",
            "target_type",
            "target_value",
            "target_display",
            "phone_masked",
            "scam_type",
            "incident_date",
            "story",
            "region",
            "damage_amount",
            "status",
            "moderator_comment",
            "created_at",
        )

    def get_phone_masked(self, obj) -> str:
        return obj.scammer_number.phone_masked if obj.scammer_number_id else ""

    def get_target_display(self, obj) -> str:
        if obj.scammer_number_id:
            return obj.scammer_number.phone_masked
        return obj.target_value


class ModeratorReportSerializer(MyReportSerializer):
    reporter_id = serializers.UUIDField(source="user_id")
    reporter_name = serializers.CharField(source="user.full_name")
    phone_full = serializers.SerializerMethodField()
    number_id = serializers.SerializerMethodField()
    number_status = serializers.SerializerMethodField()
    approved_reports_count = serializers.SerializerMethodField()
    number_verified = serializers.SerializerMethodField()

    class Meta(MyReportSerializer.Meta):
        fields = (
            *MyReportSerializer.Meta.fields,
            "reporter_id",
            "reporter_name",
            "phone_full",
            "number_id",
            "number_status",
            "approved_reports_count",
            "number_verified",
            "moderated_at",
        )

    def get_phone_full(self, obj) -> str:
        if not obj.scammer_number_id:
            return ""
        try:
            return decrypt_phone(obj.scammer_number.phone_encrypted)
        except ValueError:
            return obj.scammer_number.phone_masked

    def get_number_verified(self, obj) -> bool:
        return (
            obj.scammer_number_id is not None
            and obj.scammer_number.status == ScammerNumber.Status.VERIFIED_SCAMMER
        )

    def get_number_id(self, obj):
        return obj.scammer_number_id

    def get_number_status(self, obj):
        return obj.scammer_number.status if obj.scammer_number_id else ""

    def get_approved_reports_count(self, obj):
        return obj.scammer_number.approved_reports_count if obj.scammer_number_id else 0


class ModerationNumberSerializer(serializers.ModelSerializer):
    number_id = serializers.UUIDField(source="id")
    phone_full = serializers.SerializerMethodField()
    scam_types = serializers.SerializerMethodField()
    latest_reports = serializers.SerializerMethodField()
    number_verified = serializers.SerializerMethodField()

    class Meta:
        model = ScammerNumber
        fields = (
            "number_id",
            "phone_masked",
            "phone_full",
            "status",
            "approved_reports_count",
            "number_verified",
            "scam_types",
            "first_reported_at",
            "last_reported_at",
            "verified_at",
            "latest_reports",
        )

    def get_phone_full(self, obj) -> str:
        try:
            return decrypt_phone(obj.phone_encrypted)
        except ValueError:
            return obj.phone_masked

    def get_scam_types(self, obj) -> list[str]:
        return list(
            obj.reports.filter(status=CommunityReport.Status.APPROVED)
            .values_list("scam_type", flat=True)
            .distinct()
        )

    def get_latest_reports(self, obj) -> list[dict]:
        reports = obj.reports.select_related("user").order_by("-created_at")[:5]
        return ModeratorReportSerializer(reports, many=True).data

    def get_number_verified(self, obj) -> bool:
        return obj.status == ScammerNumber.Status.VERIFIED_SCAMMER


class ModerateReportSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=(
            CommunityReport.Status.APPROVED,
            CommunityReport.Status.REJECTED,
        )
    )
    moderator_comment = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
    )

    def update(self, instance, validated_data):
        return moderate_report(
            report=instance,
            moderator=self.context["request"].user,
            **validated_data,
        )


class VerifyNumberSerializer(serializers.Serializer):
    verified = serializers.BooleanField()

    def update(self, instance, validated_data):
        return set_verified_status(
            number=instance,
            moderator=self.context["request"].user,
            **validated_data,
        )


class ModerationSummarySerializer(serializers.Serializer):
    pending = serializers.IntegerField()
    approved = serializers.IntegerField()
    rejected = serializers.IntegerField()
    verified_numbers = serializers.IntegerField()
    reports_today = serializers.IntegerField()
