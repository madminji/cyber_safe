from django.contrib import admin

from .models import GameChoice, GameScenario, GameSession, GameStep, GameTurn


class GameStepInline(admin.TabularInline):
    model = GameStep
    extra = 0


@admin.register(GameScenario)
class GameScenarioAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "scam_type", "difficulty", "is_published", "order")
    list_filter = ("difficulty", "is_published", "scam_type")
    prepopulated_fields = {"slug": ("title_ru",)}
    inlines = (GameStepInline,)


class GameChoiceInline(admin.TabularInline):
    model = GameChoice
    extra = 3


@admin.register(GameStep)
class GameStepAdmin(admin.ModelAdmin):
    list_display = ("scenario", "order", "short_message")
    list_filter = ("scenario",)
    inlines = (GameChoiceInline,)

    @admin.display(description="Message")
    def short_message(self, obj):
        return obj.message_ru[:80]


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "scenario",
        "status",
        "score_percent",
        "points_awarded",
        "started_at",
    )
    list_filter = ("status", "scenario")


@admin.register(GameTurn)
class GameTurnAdmin(admin.ModelAdmin):
    list_display = ("session", "step", "points", "created_at")

