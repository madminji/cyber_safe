from django.urls import path

from .views import CertificateDetailView, CertificatePDFView, MyCertificateListView

urlpatterns = [
    path("", MyCertificateListView.as_view(), name="certificate-list"),
    path("<uuid:certificate_id>/", CertificateDetailView.as_view(), name="certificate-detail"),
    path("<uuid:certificate_id>/pdf/", CertificatePDFView.as_view(), name="certificate-pdf"),
]
