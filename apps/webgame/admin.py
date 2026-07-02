from django.contrib import admin

from .models import (
    GameAction,
    GameCharacter,
    GameMission,
    GameMissionStep,
    GameScenario3D,
    GameSession3D,
    UserGameProfile,
)


class GameMissionStepInline(admin.TabularInline):
    model = GameMissionStep
    extra = 0


@admin.register(GameCharacter)
class GameCharacterAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "role", "gender", "model_key", "is_active", "order")
    list_filter = ("role", "gender", "is_active")
    search_fields = ("name_ru", "name_uz", "model_key")


class GameMissionInline(admin.TabularInline):
    model = GameMission
    extra = 0


@admin.register(GameScenario3D)
class GameScenario3DAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "category", "is_default", "is_published", "order")
    list_filter = ("category", "is_default", "is_published")
    prepopulated_fields = {"slug": ("title_ru",)}
    inlines = [GameMissionInline]


@admin.register(GameMission)
class GameMissionAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "scenario", "difficulty", "scene_key", "max_score")
    list_filter = ("difficulty", "scene_key")
    inlines = [GameMissionStepInline]


@admin.register(UserGameProfile)
class UserGameProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "selected_character", "total_score", "missions_completed")
    search_fields = ("user__phone", "user__full_name")


@admin.register(GameSession3D)
class GameSession3DAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "scenario", "difficulty", "status", "score")
    list_filter = ("difficulty", "status")
    readonly_fields = ("started_at", "completed_at")


@admin.register(GameAction)
class GameActionAdmin(admin.ModelAdmin):
    list_display = ("session", "step", "selected_value", "correct", "points_delta")
    list_filter = ("correct",)
