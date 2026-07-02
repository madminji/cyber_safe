import uuid

from rest_framework import serializers

from .models import Choice, Question, TestAnswer
from .services import start_daily_test, start_test, submit_test


class ChoiceSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ("id", "text", "order")

    def get_text(self, obj):
        language = self.context.get("language", "ru")
        return obj.text_uz if language == "uz" else obj.text_ru


class QuestionSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()
    choices = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ("id", "text", "category", "difficulty", "choices")

    def get_text(self, obj):
        language = self.context.get("language", "ru")
        return obj.text_uz if language == "uz" else obj.text_ru

    def get_choices(self, obj):
        return ChoiceSerializer(
            obj.choices.all(),
            many=True,
            context=self.context,
        ).data


class StartTestSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=(("ru", "Русский"), ("uz", "O‘zbekcha")))

    def create(self, validated_data):
        return start_test(user=self.context["request"].user, **validated_data)


class StartDailyTestSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=(("ru", "Русский"), ("uz", "O‘zbekcha")))

    def create(self, validated_data):
        return start_daily_test(
            user=self.context["request"].user,
            **validated_data,
        )


class AnswerInputSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    choice_id = serializers.UUIDField()


class SubmitTestSerializer(serializers.Serializer):
    answers = AnswerInputSerializer(many=True)
    duration_seconds = serializers.IntegerField(min_value=1, max_value=7200)

    def create(self, validated_data):
        return submit_test(
            session_id=self.context["session_id"],
            actor=self.context["request"].user,
            **validated_data,
        )


class AnswerResultSerializer(serializers.ModelSerializer):
    question_id = serializers.UUIDField()
    selected_choice_id = serializers.UUIDField(source="choice_id")
    correct_choice_id = serializers.SerializerMethodField()
    explanation = serializers.SerializerMethodField()

    class Meta:
        model = TestAnswer
        fields = (
            "question_id",
            "selected_choice_id",
            "correct_choice_id",
            "is_correct",
            "explanation",
        )

    def get_correct_choice_id(self, obj) -> uuid.UUID | None:
        return obj.question.choices.filter(is_correct=True).values_list("id", flat=True).first()

    def get_explanation(self, obj) -> str:
        language = obj.session.language
        return obj.question.explanation_uz if language == "uz" else obj.question.explanation_ru
