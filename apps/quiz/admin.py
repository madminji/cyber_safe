from django.contrib import admin

from .models import Choice, Question, TestAnswer, TestSession


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "category", "difficulty", "is_active", "updated_at")
    list_filter = ("category", "difficulty", "is_active")
    search_fields = ("text_ru", "text_uz")
    inlines = (ChoiceInline,)

    @admin.display(description="Question")
    def short_text(self, obj):
        return obj.text_ru[:80]


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "score", "level", "started_at", "completed_at")
    list_filter = ("status", "level", "language")
    readonly_fields = ("started_at", "completed_at")


@admin.register(TestAnswer)
class TestAnswerAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "is_correct", "answered_at")
    list_filter = ("is_correct",)

