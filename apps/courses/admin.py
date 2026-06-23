from django.contrib import admin

from .models import Course, Lesson, LessonChoice, LessonProgress, LessonQuestion


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "level", "duration_minutes", "is_published", "order")
    list_filter = ("level", "is_published")
    prepopulated_fields = {"slug": ("title_ru",)}
    inlines = (LessonInline,)


class LessonChoiceInline(admin.TabularInline):
    model = LessonChoice
    extra = 4


@admin.register(LessonQuestion)
class LessonQuestionAdmin(admin.ModelAdmin):
    list_display = ("lesson", "short_text")
    inlines = (LessonChoiceInline,)

    @admin.display(description="Question")
    def short_text(self, obj):
        return obj.text_ru[:80]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed_at")
    search_fields = ("user__full_name", "lesson__title_ru")

