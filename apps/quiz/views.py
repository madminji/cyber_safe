from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import TestSession
from .serializers import (
    AnswerResultSerializer,
    QuestionSerializer,
    StartDailyTestSerializer,
    StartTestSerializer,
    SubmitTestSerializer,
)
from .services import daily_quiz_status


def session_payload(session):
    questions = [
        session_question.question
        for session_question in session.session_questions.all()
    ]
    return {
        "session_id": session.id,
        "kind": session.kind,
        "question_count": len(questions),
        "expires_in": settings.QUIZ_SESSION_TTL_SECONDS,
        "questions": QuestionSerializer(
            questions,
            many=True,
            context={"language": session.language},
        ).data,
    }


class StartTestView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = StartTestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        return Response(session_payload(session), status=201)


class DailyQuizView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StartDailyTestSerializer

    def get(self, request):
        return Response(daily_quiz_status(request.user))

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session, created = serializer.save()
        payload = session_payload(session)
        payload["created"] = created
        payload["completed"] = session.status == TestSession.Status.COMPLETED
        payload["score"] = session.score
        return Response(payload, status=201 if created else 200)


class SubmitTestView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SubmitTestSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["session_id"] = self.kwargs["session_id"]
        return context

    def post(self, request, session_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session, certificate = serializer.save()
        answers = session.answers.select_related("session", "question", "choice").prefetch_related(
            "question__choices"
        )
        return Response(
            {
                "session_id": session.id,
                "kind": session.kind,
                "score": session.score,
                "level": session.level,
                "passed": session.score >= 60,
                "certificate_id": certificate.id if certificate else None,
                "answers": AnswerResultSerializer(answers, many=True).data,
            }
        )


class TestResultView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AnswerResultSerializer
    queryset = TestSession.objects.none()

    @extend_schema(responses=AnswerResultSerializer(many=True))
    def get(self, request, session_id):
        try:
            session = TestSession.objects.get(
                id=session_id,
                status=TestSession.Status.COMPLETED,
            )
        except TestSession.DoesNotExist:
            return Response({"detail": "Result not found."}, status=404)

        if session.user_id and request.user != session.user:
            return Response({"detail": "Result not found."}, status=404)

        answers = session.answers.select_related("session", "question", "choice").prefetch_related(
            "question__choices"
        )
        return Response(
            {
                "session_id": session.id,
                "score": session.score,
                "level": session.level,
                "answers": AnswerResultSerializer(answers, many=True).data,
            }
        )
