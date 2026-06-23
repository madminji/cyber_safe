from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import TestSession
from .serializers import (
    AnswerResultSerializer,
    QuestionSerializer,
    StartTestSerializer,
    SubmitTestSerializer,
)


class StartTestView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = StartTestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        questions = [
            session_question.question
            for session_question in session.session_questions.all()
        ]
        return Response(
            {
                "session_id": session.id,
                "question_count": len(questions),
                "expires_in": settings.QUIZ_SESSION_TTL_SECONDS,
                "questions": QuestionSerializer(
                    questions,
                    many=True,
                    context={"language": session.language},
                ).data,
            },
            status=201,
        )


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
