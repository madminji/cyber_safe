import uuid

from django.conf import settings
from django.db import models


class GameCharacter(models.Model):
    class Role(models.TextChoices):
        ANALYST = "analyst", "Analyst"
        DEFENDER = "defender", "Defender"
        INVESTIGATOR = "investigator", "Investigator"
        MENTOR = "mentor", "Mentor"

    class Gender(models.TextChoices):
        FEMALE = "female", "Female"
        MALE = "male", "Male"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_ru = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    role = models.CharField(max_length=30, choices=Role.choices)
    gender = models.CharField(max_length=20, choices=Gender.choices)
    description_ru = models.TextField()
    description_uz = models.TextField()
    model_key = models.CharField(max_length=100, unique=True)
    color_primary = models.CharField(max_length=20, default="#2563eb")
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "name_ru")

    def __str__(self):
        return self.name_ru


class UserGameProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="webgame_profile",
        on_delete=models.CASCADE,
    )
    selected_character = models.ForeignKey(
        GameCharacter,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    total_score = models.PositiveIntegerField(default=0)
    missions_completed = models.PositiveIntegerField(default=0)
    last_played_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-total_score", "user_id")

    def __str__(self):
        return f"{self.user}: {self.total_score}"


class GameScenario3D(models.Model):
    class Category(models.TextChoices):
        PHISHING = "phishing", "Phishing"
        SOCIAL = "social_engineering", "Social engineering"
        PASSWORD = "password_safety", "Password safety"
        ACCOUNT = "account_security", "Account security"
        PRIVACY = "privacy_protection", "Privacy protection"
        SAFE_CLICKING = "safe_clicking", "Safe clicking"
        LOGIN = "suspicious_login", "Suspicious login"

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
    category = models.CharField(max_length=40, choices=Category.choices)
    is_default = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "title_ru")

    def __str__(self):
        return self.title_ru


class GameMission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(
        GameScenario3D,
        related_name="missions",
        on_delete=models.CASCADE,
    )
    difficulty = models.CharField(max_length=10, choices=GameScenario3D.Difficulty.choices)
    title_ru = models.CharField(max_length=200)
    title_uz = models.CharField(max_length=200)
    scene_key = models.CharField(max_length=100)
    rules = models.JSONField(default=dict, blank=True)
    max_score = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ("scenario__order", "difficulty", "title_ru")
        constraints = [
            models.UniqueConstraint(
                fields=("scenario", "difficulty"),
                name="unique_webgame_mission_per_difficulty",
            )
        ]

    def __str__(self):
        return f"{self.scenario.title_ru}: {self.difficulty}"


class GameMissionStep(models.Model):
    class TaskType(models.TextChoices):
        SELECT_OBJECT = "select_object", "Select object"
        DIALOGUE = "dialogue", "Dialogue"
        SECURE_ACCOUNT = "secure_account", "Secure account"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission = models.ForeignKey(
        GameMission,
        related_name="steps",
        on_delete=models.CASCADE,
    )
    order = models.PositiveSmallIntegerField()
    task_type = models.CharField(max_length=40, choices=TaskType.choices)
    prompt_ru = models.TextField()
    prompt_uz = models.TextField()
    options = models.JSONField(default=list, blank=True)
    correct_value = models.CharField(max_length=200)
    points = models.IntegerField(default=10)
    penalty = models.IntegerField(default=-5)
    feedback_correct_ru = models.TextField()
    feedback_correct_uz = models.TextField()
    feedback_wrong_ru = models.TextField()
    feedback_wrong_uz = models.TextField()

    class Meta:
        ordering = ("order",)
        constraints = [
            models.UniqueConstraint(
                fields=("mission", "order"),
                name="unique_webgame_step_order",
            )
        ]

    def __str__(self):
        return f"{self.mission}: {self.order}"


class GameSession3D(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="webgame_sessions",
        on_delete=models.CASCADE,
    )
    scenario = models.ForeignKey(GameScenario3D, on_delete=models.PROTECT)
    mission = models.ForeignKey(GameMission, on_delete=models.PROTECT)
    character = models.ForeignKey(GameCharacter, on_delete=models.PROTECT)
    difficulty = models.CharField(max_length=10, choices=GameScenario3D.Difficulty.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    score = models.IntegerField(default=0)
    max_score = models.PositiveIntegerField(default=0)
    points_awarded = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-started_at",)


class GameAction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        GameSession3D,
        related_name="actions",
        on_delete=models.CASCADE,
    )
    step = models.ForeignKey(GameMissionStep, on_delete=models.PROTECT)
    selected_value = models.CharField(max_length=300)
    correct = models.BooleanField()
    points_delta = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("session", "step"),
                name="one_webgame_action_per_step",
            )
        ]
