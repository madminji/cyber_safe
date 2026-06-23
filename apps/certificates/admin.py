from django.contrib import admin

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "level", "score", "issued_at", "is_valid")
    list_filter = ("level", "is_valid")
    search_fields = ("id", "user__full_name", "user__phone_hash")
    readonly_fields = ("id", "issued_at")

