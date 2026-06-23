from django.contrib import admin

from .models import AnalysisLog, ThreatDomain


@admin.register(ThreatDomain)
class ThreatDomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "category", "source", "is_active", "expires_at")
    list_filter = ("category", "is_active", "source")
    search_fields = ("domain",)


@admin.register(AnalysisLog)
class AnalysisLogAdmin(admin.ModelAdmin):
    list_display = ("id", "content_type", "verdict", "risk_score", "created_at")
    list_filter = ("content_type", "verdict")
    search_fields = ("content_hash", "ip_hash")
    readonly_fields = (
        "id",
        "content_hash",
        "content_type",
        "verdict",
        "risk_score",
        "reasons",
        "ip_hash",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

