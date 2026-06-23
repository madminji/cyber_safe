from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsModeratorOrAdmin

from .models import CommunityReport, ScammerNumber
from .serializers import (
    CreateReportSerializer,
    ModerateReportSerializer,
    ModerationSummarySerializer,
    ModeratorReportSerializer,
    MyReportSerializer,
    NumberCheckSerializer,
    PhoneCheckQuerySerializer,
    VerifyNumberSerializer,
)
from .services import find_number


class CheckNumberView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneCheckQuerySerializer

    @extend_schema(parameters=[PhoneCheckQuerySerializer], responses=NumberCheckSerializer)
    def get(self, request):
        query = self.get_serializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        number = find_number(query.validated_data["phone"])
        if number is None or number.approved_reports_count == 0:
            return Response(
                {
                    "found": False,
                    "status": "not_found",
                    "message": (
                        "No approved reports were found. "
                        "This does not prove that the number is safe."
                    ),
                }
            )
        return Response(
            {
                "found": True,
                **NumberCheckSerializer(number).data,
            }
        )


class CreateReportView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateReportSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        return Response(MyReportSerializer(report).data, status=201)


class MyReportListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MyReportSerializer
    queryset = CommunityReport.objects.none()

    def get_queryset(self):
        return CommunityReport.objects.filter(user=self.request.user).select_related(
            "scammer_number"
        )


class ModeratorReportListView(ListAPIView):
    permission_classes = [IsModeratorOrAdmin]
    serializer_class = ModeratorReportSerializer
    queryset = CommunityReport.objects.none()

    def get_queryset(self):
        queryset = CommunityReport.objects.select_related("scammer_number", "user")
        status = self.request.query_params.get("status")
        if status in CommunityReport.Status.values:
            queryset = queryset.filter(status=status)
        return queryset


class ModerationSummaryView(GenericAPIView):
    permission_classes = [IsModeratorOrAdmin]
    serializer_class = ModerationSummarySerializer

    @extend_schema(
        operation_id="scammer_moderation_summary",
        responses=ModerationSummarySerializer,
    )
    def get(self, request):
        counts = {
            item["status"]: item["count"]
            for item in CommunityReport.objects.values("status").annotate(
                count=Count("id")
            )
        }
        return Response(
            {
                "pending": counts.get(CommunityReport.Status.PENDING, 0),
                "approved": counts.get(CommunityReport.Status.APPROVED, 0),
                "rejected": counts.get(CommunityReport.Status.REJECTED, 0),
                "verified_numbers": ScammerNumber.objects.filter(
                    status=ScammerNumber.Status.VERIFIED_SCAMMER
                ).count(),
                "reports_today": CommunityReport.objects.filter(
                    created_at__date=timezone.localdate()
                ).count(),
            }
        )


class ModerateReportView(GenericAPIView):
    permission_classes = [IsModeratorOrAdmin]
    serializer_class = ModerateReportSerializer

    def patch(self, request, report_id):
        try:
            report = CommunityReport.objects.get(id=report_id)
        except CommunityReport.DoesNotExist:
            return Response({"detail": "Report not found."}, status=404)
        serializer = self.get_serializer(report, data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        return Response(ModeratorReportSerializer(report).data)


class ScammerStatsView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ModeratorReportSerializer

    @extend_schema(operation_id="scammer_database_statistics")
    def get(self, request):
        approved = CommunityReport.objects.filter(status=CommunityReport.Status.APPROVED)
        by_type = list(
            approved.values("scam_type")
            .annotate(count=Count("id"), damage_amount=Sum("damage_amount"))
            .order_by("-count")
        )
        by_region = list(
            approved.values("region").annotate(count=Count("id")).order_by("-count")
        )
        by_month = list(
            approved.annotate(month=TruncMonth("incident_date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        return Response(
            {
                "approved_reports": approved.count(),
                "by_type": by_type,
                "by_region": by_region,
                "by_month": by_month,
            }
        )


class VerifyNumberView(GenericAPIView):
    permission_classes = [IsModeratorOrAdmin]
    serializer_class = VerifyNumberSerializer

    def patch(self, request, number_id):
        try:
            number = ScammerNumber.objects.get(id=number_id)
        except ScammerNumber.DoesNotExist:
            return Response({"detail": "Number not found."}, status=404)
        serializer = self.get_serializer(number, data=request.data)
        serializer.is_valid(raise_exception=True)
        number = serializer.save()
        return Response(
            {
                "number_id": number.id,
                "phone_masked": number.phone_masked,
                "status": number.status,
                "verified_at": number.verified_at,
            }
        )
