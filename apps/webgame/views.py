from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import GameCharacter, GameScenario3D, GameSession3D, UserGameProfile
from .serializers import (
    ActionResultSerializer,
    CharacterSerializer,
    CompleteSessionSerializer,
    GameProfileSerializer,
    GameSession3DSerializer,
    LeaderboardEntrySerializer,
    SaveCharacterSerializer,
    Scenario3DSerializer,
    StartWebGameSerializer,
    SubmitActionSerializer,
)
from .services import (
    complete_session,
    get_or_create_profile,
    localized,
    save_selected_character,
    session_review_payload,
    start_session,
    submit_action,
)


def requested_language(request):
    language = request.query_params.get("language")
    return language if language in {"ru", "uz"} else "ru"


class CharacterListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CharacterSerializer

    def get(self, request):
        characters = GameCharacter.objects.filter(is_active=True)
        return Response(
            self.get_serializer(
                characters,
                many=True,
                context={"language": requested_language(request)},
            ).data
        )


class GameProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GameProfileSerializer

    def get(self, request):
        return Response(
            self.get_serializer(
                get_or_create_profile(request.user),
                context={"language": requested_language(request)},
            ).data
        )


class SaveCharacterView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaveCharacterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = save_selected_character(
            user=request.user,
            character_id=serializer.validated_data["character_id"],
        )
        return Response(GameProfileSerializer(profile).data)


class Scenario3DListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = Scenario3DSerializer

    def get(self, request):
        base = GameScenario3D.objects.filter(is_published=True).annotate(
            missions_count=Count("missions")
        )
        if request.user.is_authenticated:
            scenarios = base
            for scenario in scenarios:
                scenario.locked = False
        else:
            scenarios = base.filter(is_default=True)
            for scenario in scenarios:
                scenario.locked = False
        return Response(
            self.get_serializer(
                scenarios,
                many=True,
                context={"language": requested_language(request)},
            ).data
        )


class StartWebGameView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = StartWebGameSerializer

    @extend_schema(responses=GameSession3DSerializer)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = start_session(
            user=request.user,
            scenario_id=serializer.validated_data["scenario_id"],
            character_id=serializer.validated_data["character_id"],
        )
        session = (
            GameSession3D.objects.select_related(
                "scenario",
                "mission",
                "character",
            )
            .prefetch_related("mission__steps")
            .get(id=session.id)
        )
        return Response(
            GameSession3DSerializer(
                session,
                context={"language": requested_language(request)},
            ).data,
            status=201,
        )


class SubmitActionView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SubmitActionSerializer

    @extend_schema(responses=ActionResultSerializer)
    def post(self, request, session_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session, step, correct, points_delta, completed = submit_action(
            session_id=session_id,
            user=request.user,
            step_id=serializer.validated_data["mission_step_id"],
            selected_value=serializer.validated_data["selected_value"],
        )
        language = requested_language(request)
        feedback = localized(
            step,
            "feedback_correct" if correct else "feedback_wrong",
            language,
        )
        return Response(
            {
                "correct": correct,
                "points_delta": points_delta,
                "score": session.score,
                "feedback": feedback,
                "completed": completed,
            }
        )


class CompleteWebGameView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CompleteSessionSerializer

    def post(self, request, session_id):
        session = complete_session(session_id=session_id, user=request.user)
        session = (
            GameSession3D.objects.select_related("scenario", "mission", "character")
            .prefetch_related("mission__steps", "actions__step")
            .get(id=session.id)
        )
        return Response(session_review_payload(session, requested_language(request)))


class WebGameResultView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CompleteSessionSerializer

    def get(self, request, session_id):
        try:
            session = (
                GameSession3D.objects.select_related("scenario", "mission", "character")
                .prefetch_related("mission__steps", "actions__step")
                .get(id=session_id)
            )
        except GameSession3D.DoesNotExist:
            return Response({"detail": "Game result not found."}, status=404)
        if session.user_id and (
            not request.user.is_authenticated or request.user.id != session.user_id
        ):
            return Response({"detail": "Game result not found."}, status=404)
        if session.status != GameSession3D.Status.COMPLETED:
            return Response({"detail": "Game session is not completed."}, status=400)
        return Response(session_review_payload(session, requested_language(request)))


class LeaderboardView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LeaderboardEntrySerializer

    def get(self, request):
        profiles = UserGameProfile.objects.select_related("user").order_by(
            "-total_score",
            "-missions_completed",
        )[:50]
        rows = [
            {
                "rank": index,
                "user_name": profile.user.full_name
                or profile.user.phone_masked
                or f"Player {index}",
                "total_score": profile.total_score,
                "missions_completed": profile.missions_completed,
            }
            for index, profile in enumerate(profiles, start=1)
        ]
        return Response(self.get_serializer(rows, many=True).data)
