from django.contrib import admin
from django.utils import timezone

from .models import CommunityReport, ScammerNumber
from .services import recalculate_number


@admin.register(ScammerNumber)
class ScammerNumberAdmin(admin.ModelAdmin):
    list_display = (
        "phone_masked",
        "status",
        "approved_reports_count",
        "first_reported_at",
        "last_reported_at",
    )
    list_filter = ("status",)
    search_fields = ("phone_hash", "phone_masked")
    readonly_fields = (
        "phone_hash",
        "phone_encrypted",
        "phone_masked",
        "approved_reports_count",
        "first_reported_at",
        "last_reported_at",
        "created_at",
        "updated_at",
    )


@admin.register(CommunityReport)
class CommunityReportAdmin(admin.ModelAdmin):
    list_display = (
        "scammer_number",
        "scam_type",
        "region",
        "status",
        "created_at",
        "moderated_by",
    )
    list_filter = ("status", "scam_type", "region")
    search_fields = ("scammer_number__phone_hash", "story")
    readonly_fields = ("created_at", "updated_at")
    actions = ("approve_reports", "reject_reports")

    @admin.action(description="Approve selected reports")
    def approve_reports(self, request, queryset):
        numbers = set()
        queryset.update(
            status=CommunityReport.Status.APPROVED,
            moderated_by=request.user,
            moderated_at=timezone.now(),
        )
        for report in queryset.select_related("scammer_number"):
            numbers.add(report.scammer_number)
        for number in numbers:
            recalculate_number(number)

    @admin.action(description="Reject selected reports")
    def reject_reports(self, request, queryset):
        numbers = set()
        queryset.update(
            status=CommunityReport.Status.REJECTED,
            moderated_by=request.user,
            moderated_at=timezone.now(),
        )
        for report in queryset.select_related("scammer_number"):
            numbers.add(report.scammer_number)
        for number in numbers:
            recalculate_number(number)
