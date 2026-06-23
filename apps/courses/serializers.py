from rest_framework import serializers

from .models import Course, Lesson, LessonChoice


def localized(obj, field, language):
    return getattr(obj, f"{field}_{language}")


class CourseListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    lessons_count = serializers.IntegerField(read_only=True)
    completed_lessons = serializers.IntegerField(read_only=True)
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "level",
            "duration_minutes",
            "lessons_count",
            "completed_lessons",
            "progress_percent",
        )

    def get_title(self, obj) -> str:
        return localized(obj, "title", self.context["language"])

    def get_description(self, obj) -> str:
        return localized(obj, "description", self.context["language"])

    def get_progress_percent(self, obj) -> int:
        if not obj.lessons_count:
            return 0
        return round(obj.completed_lessons * 100 / obj.lessons_count)


class LessonListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "summary",
            "duration_minutes",
            "order",
            "completed",
        )

    def get_title(self, obj) -> str:
        return localized(obj, "title", self.context["language"])

    def get_summary(self, obj) -> str:
        return localized(obj, "summary", self.context["language"])

    def get_completed(self, obj) -> bool:
        completed_ids = self.context.get("completed_ids", set())
        return obj.id in completed_ids


class CourseDetailSerializer(CourseListSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta(CourseListSerializer.Meta):
        fields = (*CourseListSerializer.Meta.fields, "lessons")

    def get_lessons(self, obj) -> list[dict]:
        return LessonListSerializer(
            obj.lessons.all(),
            many=True,
            context=self.context,
        ).data


class LessonChoiceSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()

    class Meta:
        model = LessonChoice
        fields = ("id", "text", "order")

    def get_text(self, obj) -> str:
        return localized(obj, "text", self.context["language"])


class LessonDetailSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    question = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course_id",
            "title",
            "summary",
            "content",
            "video_url",
            "duration_minutes",
            "order",
            "completed",
            "question",
        )

    def get_title(self, obj) -> str:
        return localized(obj, "title", self.context["language"])

    def get_summary(self, obj) -> str:
        return localized(obj, "summary", self.context["language"])

    def get_content(self, obj) -> str:
        return localized(obj, "content", self.context["language"])

    def get_video_url(self, obj) -> str:
        return localized(obj, "video_url", self.context["language"])

    def get_completed(self, obj) -> bool:
        return self.context.get("completed", False)

    def get_question(self, obj) -> dict | None:
        if not hasattr(obj, "question"):
            return None
        question = obj.question
        language = self.context["language"]
        return {
            "text": localized(question, "text", language),
            "choices": LessonChoiceSerializer(
                question.choices.all(),
                many=True,
                context={"language": language},
            ).data,
        }


class LessonAnswerSerializer(serializers.Serializer):
    choice_id = serializers.UUIDField()


class LessonAnswerResultSerializer(serializers.Serializer):
    correct = serializers.BooleanField()
    completed = serializers.BooleanField()
    completed_now = serializers.BooleanField()
    explanation = serializers.CharField()
