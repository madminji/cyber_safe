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
        if request:
            scheme = request.headers.get("x-forwarded-proto", request.scheme)
            host = request.get_host()
            if host.startswith("127.0.0.1:8000") or host.startswith("localhost:8000"):
                host = host.replace(":8000", ":3000")
            return f"{scheme}://{host}/certificates/verify/{obj.id}"
        return f"/certificates/verify/{obj.id}"

    def get_pdf_url(self, obj) -> str:
        request = self.context.get("request")
        if request:
            user = getattr(request, "user", None)
            can_download = (
                user
                and user.is_authenticated
                and (obj.user_id == user.id or getattr(user, "role", "") == "admin")
            )
            if not can_download:
                return ""
        path = f"/api/v1/certificates/{obj.id}/pdf/"
        return request.build_absolute_uri(path) if request else path
