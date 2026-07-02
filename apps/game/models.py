import uuid

from django.conf import settings
from django.db import models


class GameScenario(models.Model):
    class InterfaceType(models.TextChoices):
        CHAT = "chat", "Messenger chat"
        CALL = "call", "Phone call"
        WEBSITE = "website", "Website"

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=100, unique=True)
    title_ru = models.CharField(max_length=200)
    title_uz = models.CharField(max_length=200)
    description_ru = models.TextField()
    description_uz = models.TextField()
    scam_type = models.CharField(max_length=40)
    interface_type = models.CharField(
        max_length=12,
        choices=InterfaceType.choices,
        default=InterfaceType.CHAT,
    )
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ("order", "title_ru")

    def __str__(self):
        return self.title_ru


class GameStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(
        GameScenario,
        related_name="steps",
        on_delete=models.CASCADE,
    )
    order = models.PositiveSmallIntegerField()
    message_ru = models.TextField()
    message_uz = models.TextField()
    tactic_ru = models.CharField(max_length=200)
    tactic_uz = models.CharField(max_length=200)

    class Meta:
        ordering = ("order",)
        constraints = [
            models.UniqueConstraint(
                fields=("scenario", "order"),
                name="unique_game_step_order",
            )
        ]

    def __str__(self):
        return f"{self.scenario.title_ru}: {self.order}"


class GameChoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    step = models.ForeignKey(GameStep, related_name="choices", on_delete=models.CASCADE)
    text_ru = models.CharField(max_length=400)
    text_uz = models.CharField(max_length=400)
    feedback_ru = models.TextField()
    feedback_uz = models.TextField()
    points = models.SmallIntegerField(default=0)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order",)


class GameSession(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="game_sessions",
        on_delete=models.CASCADE,
    )
    scenario = models.ForeignKey(
        GameScenario,
        related_name="sessions",
        on_delete=models.PROTECT,
    )
    current_step = models.ForeignKey(
        GameStep,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    current_message = models.TextField(blank=True)
    language = models.CharField(max_length=5, choices=(("ru", "Русский"), ("uz", "O‘zbekcha")))
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    score = models.IntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    score_percent = models.PositiveSmallIntegerField(null=True, blank=True)
    points_awarded = models.PositiveSmallIntegerField(default=0)
    ai_analysis = models.TextField(blank=True)
    ai_model = models.CharField(max_length=100, blank=True)
    ai_used = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class GameTurn(models.Model):
    session = models.ForeignKey(
        GameSession,
        related_name="turns",
        on_delete=models.CASCADE,
    )
    step = models.ForeignKey(GameStep, on_delete=models.PROTECT)
    choice = models.ForeignKey(GameChoice, on_delete=models.PROTECT)
    custom_text = models.TextField(blank=True)
    points = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("session", "step"),
                name="one_turn_per_game_step",
            )
        ]
