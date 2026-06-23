from rest_framework import serializers

from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    verification_url = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = (
            "id",
            "owner_name",
            "level",
            "score",
            "issued_at",
            "is_valid",
            "verification_url",
            "pdf_url",
        )

    def get_owner_name(self, obj) -> str:
        return obj.user.full_name or obj.user.phone_masked

    def get_verification_url(self, obj) -> str:
        request = self.context.get("request")
        path = f"/api/v1/certificates/{obj.id}/"
        return request.build_absolute_uri(path) if request else path

    def get_pdf_url(self, obj) -> str:
        request = self.context.get("request")
        path = f"/api/v1/certificates/{obj.id}/pdf/"
        return request.build_absolute_uri(path) if request else path
