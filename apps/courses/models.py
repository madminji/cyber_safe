import uuid

from django.conf import settings
from django.db import models


class Course(models.Model):
    class Level(models.TextChoices):
        BASIC = "basic", "Basic"
        ADVANCED = "advanced", "Advanced"
        EXPERT = "expert", "Expert"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=100, unique=True)
    title_ru = models.CharField(max_length=200)
    title_uz = models.CharField(max_length=200)
    description_ru = models.TextField()
    description_uz = models.TextField()
    level = models.CharField(max_length=12, choices=Level.choices)
    duration_minutes = models.PositiveIntegerField(default=30)
    is_published = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "title_ru")

    def __str__(self):
        return self.title_ru


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    slug = models.SlugField(max_length=140, blank=True, db_index=True)
    title_ru = models.CharField(max_length=200)
    title_uz = models.CharField(max_length=200)
    summary_ru = models.TextField()
    summary_uz = models.TextField()
    module_slug = models.SlugField(max_length=140, blank=True, db_index=True)
    module_title_ru = models.CharField(max_length=160, blank=True)
    module_title_uz = models.CharField(max_length=160, blank=True)
    content_ru = models.TextField()
    content_uz = models.TextField()
    video_url_ru = models.URLField(blank=True)
    video_url_uz = models.URLField(blank=True)
    duration_minutes = models.PositiveSmallIntegerField(default=5)
    order = models.PositiveSmallIntegerField()
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ("order",)
        constraints = [
            models.UniqueConstraint(
                fields=("course", "order"),
                name="unique_lesson_order_per_course",
            ),
            models.UniqueConstraint(
                fields=("course", "slug"),
                condition=~models.Q(slug=""),
                name="unique_lesson_slug_per_course",
            )
        ]

    def __str__(self):
        return f"{self.course.title_ru}: {self.title_ru}"

    @property
    def question(self):
        return self.questions.order_by("order", "id").first()


class LessonBlock(models.Model):
    class Type(models.TextChoices):
        THEORY = "theory", "Theory"
        DEFINITION = "definition", "Definition"
        EXAMPLE = "example", "Example"
        WARNING = "warning", "Warning"
        NOTE = "note", "Note"
        CODE = "code", "Code"
        CHECKLIST = "checklist", "Checklist"
        TASK = "task", "Task"
        QUIZ = "quiz", "Quiz"
        MATERIALS = "materials", "Materials"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, related_name="blocks", on_delete=models.CASCADE)
    type = models.CharField(max_length=24, choices=Type.choices)
    title_ru = models.CharField(max_length=200, blank=True)
    title_uz = models.CharField(max_length=200, blank=True)
    body_ru = models.TextField(blank=True)
    body_uz = models.TextField(blank=True)
    data = models.JSONField(default=dict, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.lesson.title_ru}: {self.type} #{self.order}"


class LessonTask(models.Model):
    class Type(models.TextChoices):
        TEXT = "text", "Text"
        CHECKLIST = "checklist", "Checklist"
        SORTING = "sorting", "Sorting"
        SCENARIO = "scenario", "Scenario"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, related_name="tasks", on_delete=models.CASCADE)
    type = models.CharField(max_length=24, choices=Type.choices, default=Type.TEXT)
    title_ru = models.CharField(max_length=200)
    title_uz = models.CharField(max_length=200, blank=True)
    instruction_ru = models.TextField()
    instruction_uz = models.TextField(blank=True)
    data = models.JSONField(default=dict, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.lesson.title_ru}: {self.title_ru}"


class LessonQuestion(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        related_name="questions",
        on_delete=models.CASCADE,
    )
    order = models.PositiveSmallIntegerField(default=0)
    text_ru = models.TextField()
    text_uz = models.TextField()
    explanation_ru = models.TextField()
    explanation_uz = models.TextField()

    def __str__(self):
        return self.text_ru[:80]


class LessonChoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        LessonQuestion,
        related_name="choices",
        on_delete=models.CASCADE,
    )
    text_ru = models.CharField(max_length=300)
    text_uz = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order",)


class LessonProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="lesson_progress",
        on_delete=models.CASCADE,
    )
    lesson = models.ForeignKey(
        Lesson,
        related_name="progress_records",
        on_delete=models.CASCADE,
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "lesson"),
                name="unique_lesson_progress_per_user",
            )
        ]
