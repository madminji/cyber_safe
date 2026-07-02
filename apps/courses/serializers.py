from rest_framework import serializers

from .models import Course, Lesson, LessonBlock, LessonChoice, LessonTask


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
    module_title = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "summary",
            "module_title",
            "duration_minutes",
            "order",
            "completed",
        )

    def get_title(self, obj) -> str:
        return localized(obj, "title", self.context["language"])

    def get_summary(self, obj) -> str:
        return localized(obj, "summary", self.context["language"])

    def get_module_title(self, obj) -> str:
        return localized(obj, "module_title", self.context["language"])

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


class LessonBlockSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()

    class Meta:
        model = LessonBlock
        fields = ("id", "type", "title", "body", "data", "order")

    def get_title(self, obj) -> str:
        return localized(obj, "title", self.context["language"])

    def get_body(self, obj) -> str:
        return localized(obj, "body", self.context["language"])


class LessonTaskSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    instruction = serializers.SerializerMethodField()

    class Meta:
        model = LessonTask
        fields = ("id", "type", "title", "instruction", "data", "order")

    def get_title(self, obj) -> str:
        return localized(obj, "title", self.context["language"])

    def get_instruction(self, obj) -> str:
        return localized(obj, "instruction", self.context["language"])


class LessonDetailSerializer(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    course_lessons = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    question = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()
    blocks = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course_id",
            "course_title",
            "course_lessons",
            "title",
            "summary",
            "content",
            "video_url",
            "duration_minutes",
            "order",
            "completed",
            "question",
            "questions",
            "blocks",
            "tasks",
        )

    def get_title(self, obj) -> str:
        return localized(obj, "title", self.context["language"])

    def get_course_title(self, obj) -> str:
        return localized(obj.course, "title", self.context["language"])

    def get_course_lessons(self, obj) -> list[dict]:
        return LessonListSerializer(
            obj.course.lessons.filter(is_published=True),
            many=True,
            context=self.context,
        ).data

    def get_summary(self, obj) -> str:
        return localized(obj, "summary", self.context["language"])

    def get_content(self, obj) -> str:
        return localized(obj, "content", self.context["language"])

    def get_video_url(self, obj) -> str:
        return localized(obj, "video_url", self.context["language"])

    def get_completed(self, obj) -> bool:
        return self.context.get("completed", False)

    def get_question(self, obj) -> dict | None:
        question = obj.question
        if not question:
            return None
        return self._serialize_question(question)

    def get_questions(self, obj) -> list[dict]:
        return [self._serialize_question(question) for question in obj.questions.all()]

    def _serialize_question(self, question) -> dict:
        language = self.context["language"]
        return {
            "text": localized(question, "text", language),
            "choices": LessonChoiceSerializer(
                question.choices.all(),
                many=True,
                context={"language": language},
            ).data,
        }

    def get_blocks(self, obj) -> list[dict]:
        return LessonBlockSerializer(
            obj.blocks.all(),
            many=True,
            context=self.context,
        ).data

    def get_tasks(self, obj) -> list[dict]:
        return LessonTaskSerializer(
            obj.tasks.all(),
            many=True,
            context=self.context,
        ).data


class LessonAnswerSerializer(serializers.Serializer):
    choice_id = serializers.UUIDField()


class LessonAnswerResultSerializer(serializers.Serializer):
    correct = serializers.BooleanField()
    completed = serializers.BooleanField()
    completed_now = serializers.BooleanField()
    explanation = serializers.CharField()


class LessonImportUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=False)
    payload = serializers.JSONField(required=False)

    def validate(self, attrs):
        if not attrs.get("file") and "payload" not in attrs:
            raise serializers.ValidationError(
                {"detail": "Upload a JSON file or send a JSON payload."}
            )
        if attrs.get("file") and "payload" in attrs:
            raise serializers.ValidationError(
                {"detail": "Send either file or payload, not both."}
            )
        return attrs
