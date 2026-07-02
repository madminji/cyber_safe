from rest_framework import serializers

from .models import (
    GameCharacter,
    GameMissionStep,
    GameScenario3D,
    GameSession3D,
    UserGameProfile,
)
from .services import localized


class CharacterSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = GameCharacter
        fields = (
            "id",
            "name",
            "role",
            "gender",
            "description",
            "model_key",
            "color_primary",
        )

    def get_name(self, obj):
        return localized(obj, "name", self.context["language"])

    def get_description(self, obj):
        return localized(obj, "description", self.context["language"])


class GameProfileSerializer(serializers.ModelSerializer):
    selected_character_id = serializers.UUIDField(
        allow_null=True,
        read_only=True,
    )
    recent_sessions = serializers.SerializerMethodField()

    class Meta:
        model = UserGameProfile
        fields = (
            "selected_character_id",
            "total_score",
            "missions_completed",
            "last_played_at",
            "recent_sessions",
        )

    def get_recent_sessions(self, obj):
        language = self.context.get("language", "ru")
        sessions = (
            obj.user.webgame_sessions.select_related("scenario", "mission", "character")
            .filter(status=GameSession3D.Status.COMPLETED)
            .order_by("-completed_at")[:5]
        )
        return [
            {
                "id": session.id,
                "scenario_title": localized(session.scenario, "title", language),
                "difficulty": session.difficulty,
                "score": session.score,
                "max_score": session.max_score,
                "points_awarded": session.points_awarded,
                "completed_at": session.completed_at,
            }
            for session in sessions
        ]


class SaveCharacterSerializer(serializers.Serializer):
    character_id = serializers.UUIDField()


class Scenario3DSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    missions_count = serializers.IntegerField(read_only=True)
    locked = serializers.BooleanField(read_only=True)

    class Meta:
        model = GameScenario3D
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "category",
            "is_default",
            "missions_count",
            "locked",
        )

    def get_title(self, obj):
        return localized(obj, "title", self.context["language"])

    def get_description(self, obj):
        return localized(obj, "description", self.context["language"])


class MissionStepSerializer(serializers.ModelSerializer):
    prompt = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

    class Meta:
        model = GameMissionStep
        fields = (
            "id",
            "order",
            "task_type",
            "prompt",
            "options",
            "points",
            "penalty",
        )

    def get_prompt(self, obj):
        return localized(obj, "prompt", self.context["language"])

    def get_options(self, obj):
        language = self.context["language"]
        return [
            {
                "value": item["value"],
                "label": item.get(f"label_{language}") or item.get("label_ru") or item["value"],
                "kind": item.get("kind", "neutral"),
                "color": item.get("color", "#93c5fd"),
                "position": item.get("position"),
            }
            for item in obj.options
        ]


class StartWebGameSerializer(serializers.Serializer):
    scenario_id = serializers.UUIDField()
    character_id = serializers.UUIDField()


class GameSession3DSerializer(serializers.ModelSerializer):
    scenario_title = serializers.SerializerMethodField()
    mission_title = serializers.SerializerMethodField()
    scene_key = serializers.SerializerMethodField()
    character = serializers.SerializerMethodField()
    steps = serializers.SerializerMethodField()

    class Meta:
        model = GameSession3D
        fields = (
            "id",
            "status",
            "scenario_title",
            "mission_title",
            "scene_key",
            "character",
            "difficulty",
            "score",
            "max_score",
            "points_awarded",
            "steps",
        )

    def get_scenario_title(self, obj):
        return localized(obj.scenario, "title", self.context["language"])

    def get_mission_title(self, obj):
        return localized(obj.mission, "title", self.context["language"])

    def get_scene_key(self, obj):
        return obj.mission.scene_key

    def get_character(self, obj):
        return CharacterSerializer(
            obj.character,
            context={"language": self.context["language"]},
        ).data

    def get_steps(self, obj):
        return MissionStepSerializer(
            obj.mission.steps.all(),
            many=True,
            context={"language": self.context["language"]},
        ).data


class SubmitActionSerializer(serializers.Serializer):
    mission_step_id = serializers.UUIDField()
    selected_value = serializers.CharField(max_length=300)


class ActionResultSerializer(serializers.Serializer):
    correct = serializers.BooleanField()
    points_delta = serializers.IntegerField()
    score = serializers.IntegerField()
    feedback = serializers.CharField()
    completed = serializers.BooleanField()


class CompleteSessionSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    score = serializers.IntegerField()
    max_score = serializers.IntegerField()
    score_percent = serializers.IntegerField()
    points_awarded = serializers.IntegerField()
    level = serializers.CharField()
    turns = serializers.ListField(required=False)


class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    user_name = serializers.CharField()
    total_score = serializers.IntegerField()
    missions_completed = serializers.IntegerField()
