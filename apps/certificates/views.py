from django.http import FileResponse
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Certificate
from .serializers import CertificateSerializer
from .services import build_certificate_pdf


class CertificateDetailView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CertificateSerializer

    @extend_schema(operation_id="certificate_verify")
    def get(self, request, certificate_id):
        try:
            certificate = Certificate.objects.select_related("user").get(id=certificate_id)
        except Certificate.DoesNotExist:
            return Response({"detail": "Certificate not found."}, status=404)
        return Response(self.get_serializer(certificate).data)


class CertificatePDFView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CertificateSerializer

    @extend_schema(operation_id="certificate_download_pdf")
    def get(self, request, certificate_id):
        try:
            certificate = Certificate.objects.select_related("user").get(
                id=certificate_id,
                is_valid=True,
            )
        except Certificate.DoesNotExist:
            return Response({"detail": "Certificate not found."}, status=404)
        return FileResponse(
            build_certificate_pdf(certificate),
            as_attachment=True,
            filename=f"cybersafe-{certificate.id}.pdf",
            content_type="application/pdf",
        )


class MyCertificateListView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CertificateSerializer

    @extend_schema(operation_id="my_certificates_list")
    def get(self, request):
        certificates = Certificate.objects.filter(user=request.user).select_related("user")
        return Response(self.get_serializer(certificates, many=True).data)
