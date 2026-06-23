from rest_framework import serializers

from .models import GameChoice, GameScenario, GameSession


def localized(obj, field, language):
    return getattr(obj, f"{field}_{language}")


class ScenarioSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    steps_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = GameScenario
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "scam_type",
            "difficulty",
            "steps_count",
        )

    def get_title(self, obj) -> str:
        return localized(obj, "title", self.context["language"])

    def get_description(self, obj) -> str:
        return localized(obj, "description", self.context["language"])


class GameChoiceSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()

    class Meta:
        model = GameChoice
        fields = ("id", "text", "order")

    def get_text(self, obj) -> str:
        return localized(obj, "text", self.context["language"])


class GameStateSerializer(serializers.ModelSerializer):
    scenario_title = serializers.SerializerMethodField()
    step_number = serializers.SerializerMethodField()
    total_steps = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    choices = serializers.SerializerMethodField()

    class Meta:
        model = GameSession
        fields = (
            "id",
            "status",
            "scenario_title",
            "step_number",
            "total_steps",
            "message",
            "choices",
            "score_percent",
            "points_awarded",
        )

    def get_scenario_title(self, obj) -> str:
        return localized(obj.scenario, "title", obj.language)

    def get_step_number(self, obj) -> int | None:
        return obj.current_step.order if obj.current_step else None

    def get_total_steps(self, obj) -> int:
        return obj.scenario.steps.count()

    def get_message(self, obj) -> str | None:
        if not obj.current_step:
            return None
        return obj.current_message or localized(obj.current_step, "message", obj.language)

    def get_choices(self, obj) -> list[dict]:
        if not obj.current_step:
            return []
        return GameChoiceSerializer(
            obj.current_step.choices.all(),
            many=True,
            context={"language": obj.language},
        ).data


class StartGameSerializer(serializers.Serializer):
    scenario_id = serializers.UUIDField()
    language = serializers.ChoiceField(choices=(("ru", "Русский"), ("uz", "O‘zbekcha")))


class AnswerGameSerializer(serializers.Serializer):
    choice_id = serializers.UUIDField()


class AnswerGameResultSerializer(serializers.Serializer):
    feedback = serializers.CharField()
    choice_points = serializers.IntegerField()
    completed = serializers.BooleanField()
    session = GameStateSerializer()


class GameResultSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    scenario_title = serializers.CharField()
    score_percent = serializers.IntegerField()
    points_awarded = serializers.IntegerField()
    level = serializers.CharField()
    ai_analysis = serializers.CharField(allow_blank=True)
    ai_used = serializers.BooleanField()
    ai_model = serializers.CharField(allow_blank=True)
    turns = serializers.ListField()
