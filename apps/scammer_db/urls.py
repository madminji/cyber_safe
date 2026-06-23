from django.urls import path

from .views import (
    CheckNumberView,
    CreateReportView,
    ModerateReportView,
    ModerationSummaryView,
    ModeratorReportListView,
    MyReportListView,
    ScammerStatsView,
    VerifyNumberView,
)

urlpatterns = [
    path("check/", CheckNumberView.as_view(), name="scammer-check"),
    path("reports/", CreateReportView.as_view(), name="scammer-report-create"),
    path("reports/my/", MyReportListView.as_view(), name="scammer-report-mine"),
    path("stats/", ScammerStatsView.as_view(), name="scammer-stats"),
    path(
        "moderation/reports/",
        ModeratorReportListView.as_view(),
        name="scammer-moderation-list",
    ),
    path(
        "moderation/summary/",
        ModerationSummaryView.as_view(),
        name="scammer-moderation-summary",
    ),
    path(
        "moderation/reports/<uuid:report_id>/",
        ModerateReportView.as_view(),
        name="scammer-moderation-detail",
    ),
    path(
        "moderation/numbers/<uuid:number_id>/verification/",
        VerifyNumberView.as_view(),
        name="scammer-number-verification",
    ),
]
