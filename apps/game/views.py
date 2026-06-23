from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .ai import enrich_game_session
from .models import GameScenario, GameSession
from .serializers import (
    AnswerGameResultSerializer,
    AnswerGameSerializer,
    GameResultSerializer,
    GameStateSerializer,
    ScenarioSerializer,
    StartGameSerializer,
)
from .services import answer_game_step, start_game


def localized(obj, field, language):
    return getattr(obj, f"{field}_{language}")


def requested_language(request):
    language = request.query_params.get("language")
    return language if language in {"ru", "uz"} else "ru"


class ScenarioListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ScenarioSerializer

    @extend_schema(operation_id="game_scenarios_list")
    def get(self, request):
        scenarios = GameScenario.objects.filter(is_published=True).annotate(
            steps_count=Count("steps")
        )
        return Response(
            self.get_serializer(
                scenarios,
                many=True,
                context={"language": requested_language(request)},
            ).data
        )


class StartGameView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StartGameSerializer

    @extend_schema(responses=GameStateSerializer)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            scenario = GameScenario.objects.get(
                id=serializer.validated_data["scenario_id"],
                is_published=True,
            )
        except GameScenario.DoesNotExist:
            return Response({"detail": "Scenario not found."}, status=404)
        session = start_game(
            user=request.user,
            scenario=scenario,
            language=serializer.validated_data["language"],
        )
        session = GameSession.objects.select_related(
            "scenario",
            "current_step",
        ).prefetch_related(
            "scenario__steps",
            "current_step__choices",
        ).get(id=session.id)
        return Response(GameStateSerializer(session).data, status=201)


class GameSessionView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GameStateSerializer

    def get(self, request, session_id):
        try:
            session = GameSession.objects.select_related(
                "scenario",
                "current_step",
            ).prefetch_related(
                "scenario__steps",
                "current_step__choices",
            ).get(id=session_id, user=request.user)
        except GameSession.DoesNotExist:
            return Response({"detail": "Game session not found."}, status=404)
        return Response(self.get_serializer(session).data)


class AnswerGameView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerGameSerializer

    @extend_schema(responses=AnswerGameResultSerializer)
    def post(self, request, session_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            session = GameSession.objects.get(id=session_id, user=request.user)
        except GameSession.DoesNotExist:
            return Response({"detail": "Game session not found."}, status=404)
        session, choice, completed = answer_game_step(
            session=session,
            user=request.user,
            choice_id=serializer.validated_data["choice_id"],
        )
        session = enrich_game_session(
            session=session,
            selected_choice=choice,
            completed=completed,
        )
        session = GameSession.objects.select_related(
            "scenario",
            "current_step",
        ).prefetch_related(
            "scenario__steps",
            "current_step__choices",
        ).get(id=session.id)
        feedback = localized(choice, "feedback", session.language)
        return Response(
            {
                "feedback": feedback,
                "choice_points": choice.points,
                "completed": completed,
                "session": GameStateSerializer(session).data,
            }
        )


class GameResultView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GameResultSerializer

    def get(self, request, session_id):
        try:
            session = GameSession.objects.select_related("scenario").prefetch_related(
                "turns__step",
                "turns__choice",
            ).get(
                id=session_id,
                user=request.user,
                status=GameSession.Status.COMPLETED,
            )
        except GameSession.DoesNotExist:
            return Response({"detail": "Game result not found."}, status=404)
        language = session.language
        score = session.score_percent or 0
        if score >= 80:
            level = "expert"
        elif score >= 55:
            level = "resistant"
        else:
            level = "vulnerable"
        turns = [
            {
                "step": turn.step.order,
                "message": localized(turn.step, "message", language),
                "answer": localized(turn.choice, "text", language),
                "feedback": localized(turn.choice, "feedback", language),
                "tactic": localized(turn.step, "tactic", language),
                "points": turn.points,
            }
            for turn in session.turns.all()
        ]
        return Response(
            {
                "session_id": session.id,
                "scenario_title": localized(session.scenario, "title", language),
                "score_percent": score,
                "points_awarded": session.points_awarded,
                "level": level,
                "ai_analysis": session.ai_analysis,
                "ai_used": session.ai_used,
                "ai_model": session.ai_model,
                "turns": turns,
            }
        )
