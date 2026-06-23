import uuid

from django.conf import settings
from django.db import models


class Question(models.Model):
    class Category(models.TextChoices):
        PHISHING = "phishing", "Phishing"
        CALL = "call", "Fraudulent call"
        SMS = "sms", "Fraudulent SMS"
        MALWARE = "malware", "Malware"
        SOCIAL_ENGINEERING = "social_engineering", "Social engineering"

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text_ru = models.TextField()
    text_uz = models.TextField()
    category = models.CharField(max_length=30, choices=Category.choices)
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
    )
    explanation_ru = models.TextField()
    explanation_uz = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text_ru[:80]


class Choice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    text_ru = models.CharField(max_length=300)
    text_uz = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.text_ru


class TestSession(models.Model):
    class Status(models.TextChoices):
        STARTED = "started", "Started"
        COMPLETED = "completed", "Completed"
        EXPIRED = "expired", "Expired"

    class Level(models.TextChoices):
        NONE = "none", "Not passed"
        BASIC = "basic", "Basic"
        ADVANCED = "advanced", "Advanced"
        EXPERT = "expert", "Expert"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="quiz_sessions",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    questions = models.ManyToManyField(Question, through="SessionQuestion")
    language = models.CharField(max_length=5, choices=(("ru", "Русский"), ("uz", "O‘zbekcha")))
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.STARTED)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.NONE)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.id} — {self.status}"


class SessionQuestion(models.Model):
    session = models.ForeignKey(
        TestSession,
        related_name="session_questions",
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ("order",)
        constraints = [
            models.UniqueConstraint(
                fields=("session", "question"),
                name="unique_question_per_quiz_session",
            ),
            models.UniqueConstraint(
                fields=("session", "order"),
                name="unique_order_per_quiz_session",
            ),
        ]


class TestAnswer(models.Model):
    session = models.ForeignKey(TestSession, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    choice = models.ForeignKey(Choice, on_delete=models.PROTECT)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("session", "question"),
                name="one_answer_per_session_question",
            )
        ]

