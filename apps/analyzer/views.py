from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import AnalysisLog
from .serializers import (
    AnalysisResultSerializer,
    SMSAnalysisInputSerializer,
    URLAnalysisInputSerializer,
)
from .services import (
    analyze_sms_value,
    analyze_url_value,
    enforce_rate_limit,
    save_analysis,
    stable_hash,
)


def client_ip(request):
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",", 1)[0].strip() or request.META.get("REMOTE_ADDR", "unknown")


PRIVACY_MESSAGES = {
    "ru": "Содержимое не сохранено. В журнал записан только необратимый хэш.",
    "uz": "Mazmun saqlanmadi. Jurnalga faqat qaytarib bo‘lmaydigan xesh yozildi.",
}


def response_data(log, result, language):
    return {
        "analysis_id": log.id,
        "verdict": result.verdict,
        "risk_score": result.risk_score,
        "reasons": result.reasons,
        "signals": result.signals,
        "privacy": PRIVACY_MESSAGES[language],
    }


class URLAnalysisView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = URLAnalysisInputSerializer

    @extend_schema(responses=AnalysisResultSerializer)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_hash = stable_hash(client_ip(request))
        enforce_rate_limit(ip_hash)
        content = serializer.validated_data["url"]
        language = serializer.validated_data["language"]
        result = analyze_url_value(content, language=language)
        log = save_analysis(
            content=content,
            content_type=AnalysisLog.ContentType.URL,
            ip_hash=ip_hash,
            result=result,
        )
        return Response(response_data(log, result, language))


class SMSAnalysisView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SMSAnalysisInputSerializer

    @extend_schema(responses=AnalysisResultSerializer)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip_hash = stable_hash(client_ip(request))
        enforce_rate_limit(ip_hash)
        content = serializer.validated_data["text"]
        language = serializer.validated_data["language"]
        result = analyze_sms_value(content, language=language)
        log = save_analysis(
            content=content,
            content_type=AnalysisLog.ContentType.SMS,
            ip_hash=ip_hash,
            result=result,
        )
        return Response(response_data(log, result, language))
